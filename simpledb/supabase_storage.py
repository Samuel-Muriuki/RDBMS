"""
Supabase PostgreSQL storage backend for SimpleDB.

Provides persistent storage using Supabase PostgreSQL instead of JSON files.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
from .exceptions import (
    TableNotFoundError, PrimaryKeyViolation, UniqueConstraintViolation,
    NotNullViolation, DataTypeError, ColumnNotFoundError
)


class SupabaseTable:
    """Represents a database table backed by PostgreSQL."""
    
    def __init__(self, name: str, columns: List[Dict[str, Any]], connection):
        self.name = name
        self.columns = columns
        self.connection = connection
        self.primary_key = None
        self.unique_columns = set()
        self.not_null_columns = set()
        
        # Process column constraints
        for col in columns:
            col_name = col['name']
            constraints = col.get('constraints', [])
            
            if 'PRIMARY KEY' in constraints:
                self.primary_key = col_name
                self.not_null_columns.add(col_name)
            
            if 'UNIQUE' in constraints:
                self.unique_columns.add(col_name)
            
            if 'NOT NULL' in constraints:
                self.not_null_columns.add(col_name)
    
    def get_column(self, name: str) -> Optional[Dict[str, Any]]:
        """Get column definition by name."""
        for col in self.columns:
            if col['name'] == name:
                return col
        return None
    
    def _map_type_to_postgres(self, col_type: str, length: Optional[int] = None) -> str:
        """Map SimpleDB types to PostgreSQL types."""
        if col_type == 'INT':
            return 'INTEGER'
        elif col_type == 'VARCHAR':
            return f'VARCHAR({length or 255})'
        elif col_type == 'BOOLEAN':
            return 'BOOLEAN'
        else:
            return 'TEXT'
    
    def _create_table_sql(self) -> str:
        """Generate CREATE TABLE SQL statement."""
        col_defs = []
        
        for col in self.columns:
            col_name = col['name']
            col_type = self._map_type_to_postgres(col['type'], col.get('length'))
            constraints = col.get('constraints', [])
            
            col_def = f'"{col_name}" {col_type}'
            
            if 'PRIMARY KEY' in constraints:
                col_def += ' PRIMARY KEY'
            if 'UNIQUE' in constraints and 'PRIMARY KEY' not in constraints:
                col_def += ' UNIQUE'
            if 'NOT NULL' in constraints and 'PRIMARY KEY' not in constraints:
                col_def += ' NOT NULL'
            
            col_defs.append(col_def)
        
        return f'CREATE TABLE IF NOT EXISTS "{self.name}" ({", ".join(col_defs)})'
    
    def create_table(self):
        """Create the table in PostgreSQL."""
        with self.connection.cursor() as cursor:
            cursor.execute(self._create_table_sql())
            self.connection.commit()
    
    def validate_value(self, column: Dict[str, Any], value: Any) -> Any:
        """Validate and convert value to correct type."""
        if value is None:
            return None
        
        col_type = column['type']
        
        if col_type == 'INT':
            if not isinstance(value, int):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    raise DataTypeError(f"Cannot convert {value!r} to INT")
            return value
        
        elif col_type == 'VARCHAR':
            if not isinstance(value, str):
                value = str(value)
            max_length = column.get('length', 255)
            if len(value) > max_length:
                raise DataTypeError(f"String too long for VARCHAR({max_length}): {len(value)} chars")
            return value
        
        elif col_type == 'BOOLEAN':
            if not isinstance(value, bool):
                if isinstance(value, str):
                    if value.upper() in ('TRUE', '1', 'YES'):
                        return True
                    elif value.upper() in ('FALSE', '0', 'NO'):
                        return False
                raise DataTypeError(f"Cannot convert {value!r} to BOOLEAN")
            return value
        
        else:
            raise DataTypeError(f"Unknown type: {col_type}")
    
    def validate_row(self, row: Dict[str, Any]):
        """Validate a row against schema and constraints."""
        # Check all columns exist
        for col_name in row.keys():
            if not self.get_column(col_name):
                raise ColumnNotFoundError(f"Column '{col_name}' does not exist in table '{self.name}'")
        
        # Check NOT NULL constraints
        for col_name in self.not_null_columns:
            if row.get(col_name) is None:
                raise NotNullViolation(f"Column '{col_name}' cannot be NULL")
    
    def insert_row(self, values: Dict[str, Any]) -> int:
        """Insert a new row and return its ID."""
        # Validate and convert types
        row = {}
        for col in self.columns:
            col_name = col['name']
            value = values.get(col_name)
            row[col_name] = self.validate_value(col, value)
        
        # Validate constraints
        self.validate_row(row)
        
        # Build INSERT query
        columns = list(row.keys())
        placeholders = [f'%s' for _ in columns]
        values_list = [row[col] for col in columns]
        
        sql = f'''
            INSERT INTO "{self.name}" ({", ".join(f'"{col}"' for col in columns)})
            VALUES ({", ".join(placeholders)})
            RETURNING *
        '''
        
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(sql, values_list)
                self.connection.commit()
                result = cursor.fetchone()
                return dict(result) if result else {}
            except psycopg2.IntegrityError as e:
                self.connection.rollback()
                if 'duplicate key' in str(e).lower():
                    if 'primary key' in str(e).lower():
                        raise PrimaryKeyViolation(f"Primary key violation: {e}")
                    else:
                        raise UniqueConstraintViolation(f"Unique constraint violation: {e}")
                raise
    
    @property
    def rows(self) -> List[Dict[str, Any]]:
        """Fetch all rows for compatibility with QueryExecutor."""
        # For compatibility with QueryExecutor which expects table.rows[i]
        # We fetch all rows and return them as a list.
        # This is not efficient for large tables but necessary for compatibility.
        sql = f'SELECT * FROM "{self.name}"'
        if self.primary_key:
            sql += f' ORDER BY "{self.primary_key}" ASC'
        
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            return [dict(row) for row in cursor.fetchall()]

    def find_rows(self, conditions: Optional[List[Dict[str, Any]]] = None) -> List[int]:
        """Find rows matching conditions. Returns list of row indexes."""
        # QueryExecutor expects list of integers (indexes)
        # We fetch matching rows and return their range
        sql = f'SELECT * FROM "{self.name}"'
        values = []
        
        if conditions:
            where_clause, values = self._build_where_clause(conditions)
            if where_clause:
                sql += f' WHERE {where_clause}'
        
        if self.primary_key:
            sql += f' ORDER BY "{self.primary_key}" ASC'
        
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, values)
            count = len(cursor.fetchall())
            return list(range(count))

    def update_row(self, row_index: int, updates: Dict[str, Any]):
        """Update a row by its index in the current fetch (simplified for compatibility)."""
        # This is tricky because indexes are not persistent in SQL.
        # QueryExecutor calls find_rows, gets indexes, then calls update_row(index, updates).
        # We need to fetch the row at that index to get its PK, then update it.
        rows = self.rows
        if row_index < 0 or row_index >= len(rows):
            return
        
        row = rows[row_index]
        if not self.primary_key:
            raise SimpleDBException("Update by index requires a primary key in Supabase storage")
        
        pk_val = row[self.primary_key]
        conditions = [{'column': self.primary_key, 'operator': '=', 'value': pk_val}]
        
        # Original update_row logic
        # Validate updates
        for col_name, value in updates.items():
            col = self.get_column(col_name)
            if not col:
                raise ColumnNotFoundError(f"Column '{col_name}' does not exist")
            updates[col_name] = self.validate_value(col, value)
        
        # Build UPDATE query
        set_clauses = [f'"{col}" = %s' for col in updates.keys()]
        where_clause, where_values = self._build_where_clause(conditions)
        
        sql = f'UPDATE "{self.name}" SET {", ".join(set_clauses)} WHERE {where_clause}'
        values = list(updates.values()) + where_values
        
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql, values)
                self.connection.commit()
            except psycopg2.IntegrityError as e:
                self.connection.rollback()
                if 'duplicate key' in str(e).lower():
                    raise UniqueConstraintViolation(f"Unique constraint violation: {e}")
                raise

    def delete_row(self, row_index: int):
        """Delete a row by its index in the current fetch."""
        rows = self.rows
        if row_index < 0 or row_index >= len(rows):
            return
        
        row = rows[row_index]
        if not self.primary_key:
            raise SimpleDBException("Delete by index requires a primary key in Supabase storage")
        
        pk_val = row[self.primary_key]
        
        sql = f'DELETE FROM "{self.name}" WHERE "{self.primary_key}" = %s'
        
        with self.connection.cursor() as cursor:
            cursor.execute(sql, (pk_val,))
            self.connection.commit()

    
    def _build_where_clause(self, conditions: List[Dict[str, Any]]) -> tuple:
        """Build WHERE clause from conditions."""
        if not conditions:
            return '', []
        
        clauses = []
        values = []
        current_logic = 'AND'
        
        for cond in conditions:
            if 'logic' in cond:
                current_logic = cond['logic']
                continue
            
            column = cond['column']
            operator = cond['operator']
            value = cond['value']
            
            # Map operators
            op_map = {
                '=': '=',
                '!=': '!=',
                '<': '<',
                '<=': '<=',
                '>': '>',
                '>=': '>='
            }
            
            if operator not in op_map:
                raise DataTypeError(f"Unknown operator: {operator}")
            
            clauses.append(f'"{column}" {op_map[operator]} %s')
            values.append(value)
        
        # Join with logic operators (simplified - assumes all same logic)
        where_clause = f' {current_logic} '.join(clauses)
        return where_clause, values
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table schema to dictionary."""
        return {
            'name': self.name,
            'columns': self.columns
        }


class SupabaseDatabase:
    """Manages multiple tables using PostgreSQL backend."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection."""
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create connection
        self.connection = psycopg2.connect(self.database_url)
        self.tables = {}
        
        # Create metadata table for storing schemas
        self._create_metadata_table()
        
        # Load existing tables
        self._load_tables()
    
    def _create_metadata_table(self):
        """Create table to store SimpleDB table schemas."""
        with self.connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS _simpledb_schemas (
                    table_name VARCHAR(255) PRIMARY KEY,
                    columns JSONB NOT NULL
                )
            ''')
            self.connection.commit()
    
    def _load_tables(self):
        """Load existing table schemas from metadata."""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT table_name, columns FROM _simpledb_schemas')
            for row in cursor.fetchall():
                table_name = row['table_name']
                columns = row['columns']
                self.tables[table_name] = SupabaseTable(table_name, columns, self.connection)
    
    def create_table(self, name: str, columns: List[Dict[str, Any]]):
        """Create a new table."""
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        
        # Create table object
        table = SupabaseTable(name, columns, self.connection)
        
        # Create actual PostgreSQL table
        table.create_table()
        
        # Store schema in metadata
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO _simpledb_schemas (table_name, columns) VALUES (%s, %s::jsonb)',
                (name, psycopg2.extras.Json(columns))
            )
            self.connection.commit()
        
        self.tables[name] = table
    
    def drop_table(self, name: str):
        """Drop a table."""
        if name not in self.tables:
            raise TableNotFoundError(f"Table '{name}' does not exist")
        
        # Drop actual table
        with self.connection.cursor() as cursor:
            cursor.execute(f'DROP TABLE IF EXISTS "{name}"')
            cursor.execute('DELETE FROM _simpledb_schemas WHERE table_name = %s', (name,))
            self.connection.commit()
        
        del self.tables[name]
    
    def get_table(self, name: str) -> SupabaseTable:
        """Get a table by name."""
        if name not in self.tables:
            raise TableNotFoundError(f"Table '{name}' does not exist")
        
        return self.tables[name]
    
    def list_tables(self) -> List[str]:
        """Get list of all table names."""
        return list(self.tables.keys())
    
    def save(self):
        """Save is automatic with PostgreSQL - no-op for compatibility."""
        pass
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Cleanup connection on deletion."""
        try:
            self.close()
        except:
            pass
