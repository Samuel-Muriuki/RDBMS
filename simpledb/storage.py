"""
Storage engine for SimpleDB.

Manages tables, rows, indexes, and persistence.
"""

import json
import os
from typing import Dict, List, Any, Optional
from .exceptions import (
    TableNotFoundError, PrimaryKeyViolation, UniqueConstraintViolation,
    NotNullViolation, DataTypeError, ColumnNotFoundError
)


class Table:
    """Represents a database table with schema and data."""
    
    def __init__(self, name: str, columns: List[Dict[str, Any]]):
        self.name = name
        self.columns = columns
        self.rows = []
        self.indexes = {}  # column_name -> {value: row_index}
        self.primary_key = None
        self.unique_columns = set()
        self.not_null_columns = set()
        
        # Process column constraints
        for col in columns:
            col_name = col['name']
            constraints = col.get('constraints', [])
            
            if 'PRIMARY KEY' in constraints:
                self.primary_key = col_name
                self.indexes[col_name] = {}
                self.not_null_columns.add(col_name)
            
            if 'UNIQUE' in constraints:
                self.unique_columns.add(col_name)
                if col_name not in self.indexes:
                    self.indexes[col_name] = {}
            
            if 'NOT NULL' in constraints:
                self.not_null_columns.add(col_name)
    
    def get_column(self, name: str) -> Optional[Dict[str, Any]]:
        """Get column definition by name."""
        for col in self.columns:
            if col['name'] == name:
                return col
        return None
    
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
    
    def validate_row(self, row: Dict[str, Any], row_index: Optional[int] = None):
        """Validate a row against schema and constraints."""
        # Check all columns exist
        for col_name in row.keys():
            if not self.get_column(col_name):
                raise ColumnNotFoundError(f"Column '{col_name}' does not exist in table '{self.name}'")
        
        # Check NOT NULL constraints
        for col_name in self.not_null_columns:
            if row.get(col_name) is None:
                raise NotNullViolation(f"Column '{col_name}' cannot be NULL")
        
        # Check PRIMARY KEY constraint
        if self.primary_key:
            pk_value = row.get(self.primary_key)
            if pk_value is not None and pk_value in self.indexes[self.primary_key]:
                existing_index = self.indexes[self.primary_key][pk_value]
                if row_index is None or existing_index != row_index:
                    raise PrimaryKeyViolation(f"Primary key '{self.primary_key}' value {pk_value} already exists")
        
        # Check UNIQUE constraints
        for col_name in self.unique_columns:
            if col_name in row and row[col_name] is not None:
                if col_name in self.indexes and row[col_name] in self.indexes[col_name]:
                    existing_index = self.indexes[col_name][row[col_name]]
                    if row_index is None or existing_index != row_index:
                        raise UniqueConstraintViolation(f"UNIQUE constraint violated for column '{col_name}' value {row[col_name]}")
    
    def insert_row(self, values: Dict[str, Any]) -> int:
        """Insert a new row and return its index."""
        # Validate and convert types
        row = {}
        for col in self.columns:
            col_name = col['name']
            value = values.get(col_name)
            row[col_name] = self.validate_value(col, value)
        
        # Validate constraints
        self.validate_row(row)
        
        # Add row
        row_index = len(self.rows)
        self.rows.append(row)
        
        # Update indexes
        for col_name in self.indexes:
            value = row.get(col_name)
            if value is not None:
                self.indexes[col_name][value] = row_index
        
        return row_index
    
    def update_row(self, row_index: int, updates: Dict[str, Any]):
        """Update an existing row."""
        if row_index < 0 or row_index >= len(self.rows):
            return
        
        old_row = self.rows[row_index].copy()
        new_row = old_row.copy()
        
        # Apply updates with type validation
        for col_name, value in updates.items():
            col = self.get_column(col_name)
            if not col:
                raise ColumnNotFoundError(f"Column '{col_name}' does not exist")
            new_row[col_name] = self.validate_value(col, value)
        
        # Validate constraints
        self.validate_row(new_row, row_index)
        
        # Update indexes (remove old values)
        for col_name in self.indexes:
            old_value = old_row.get(col_name)
            if old_value is not None and old_value in self.indexes[col_name]:
                del self.indexes[col_name][old_value]
        
        # Update row
        self.rows[row_index] = new_row
        
        # Update indexes (add new values)
        for col_name in self.indexes:
            new_value = new_row.get(col_name)
            if new_value is not None:
                self.indexes[col_name][new_value] = row_index
    
    def delete_row(self, row_index: int):
        """Delete a row by index."""
        if row_index < 0 or row_index >= len(self.rows):
            return
        
        row = self.rows[row_index]
        
        # Remove from indexes
        for col_name in self.indexes:
            value = row.get(col_name)
            if value is not None and value in self.indexes[col_name]:
                del self.indexes[col_name][value]
        
        # Mark as deleted (set to None to maintain indexes)
        self.rows[row_index] = None
    
    def find_rows(self, conditions: Optional[List[Dict[str, Any]]] = None) -> List[int]:
        """Find row indexes matching conditions."""
        if conditions is None:
            # Return all non-deleted rows
            return [i for i, row in enumerate(self.rows) if row is not None]
        
        # Evaluate conditions
        matching_indexes = []
        for i, row in enumerate(self.rows):
            if row is None:
                continue
            
            if self._evaluate_conditions(row, conditions):
                matching_indexes.append(i)
        
        return matching_indexes
    
    def _evaluate_conditions(self, row: Dict[str, Any], conditions: List[Dict[str, Any]]) -> bool:
        """Evaluate WHERE conditions for a row."""
        result = True
        current_logic = 'AND'
        
        for cond in conditions:
            if 'logic' in cond:
                current_logic = cond['logic']
                continue
            
            column = cond['column']
            operator = cond['operator']
            value = cond['value']
            
            if column not in row:
                raise ColumnNotFoundError(f"Column '{column}' not found")
            
            row_value = row[column]
            
            # Evaluate condition
            if operator == '=':
                condition_result = row_value == value
            elif operator == '!=':
                condition_result = row_value != value
            elif operator == '<':
                condition_result = row_value is not None and value is not None and row_value < value
            elif operator == '<=':
                condition_result = row_value is not None and value is not None and row_value <= value
            elif operator == '>':
                condition_result = row_value is not None and value is not None and row_value > value
            elif operator == '>=':
                condition_result = row_value is not None and value is not None and row_value >= value
            else:
                raise DataTypeError(f"Unknown operator: {operator}")
            
            # Combine with previous result
            if current_logic == 'AND':
                result = result and condition_result
            else:  # OR
                result = result or condition_result
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table to dictionary for serialization."""
        return {
            'name': self.name,
            'columns': self.columns,
            'rows': [row for row in self.rows if row is not None]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        """Create table from dictionary."""
        table = cls(data['name'], data['columns'])
        for row in data['rows']:
            table.insert_row(row)
        return table


class Database:
    """Manages multiple tables and persistence."""
    
    def __init__(self, db_file: Optional[str] = None):
        self.tables = {}
        self.db_file = db_file
        
        if db_file and os.path.exists(db_file):
            self.load()
    
    def create_table(self, name: str, columns: List[Dict[str, Any]]):
        """Create a new table."""
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        
        self.tables[name] = Table(name, columns)
    
    def drop_table(self, name: str):
        """Drop a table."""
        if name not in self.tables:
            raise TableNotFoundError(f"Table '{name}' does not exist")
        
        del self.tables[name]
    
    def get_table(self, name: str) -> Table:
        """Get a table by name."""
        if name not in self.tables:
            raise TableNotFoundError(f"Table '{name}' does not exist")
        
        return self.tables[name]
    
    def list_tables(self) -> List[str]:
        """Get list of all table names."""
        return list(self.tables.keys())
    
    def save(self):
        """Save database to file."""
        if not self.db_file:
            return
        
        data = {
            'tables': {name: table.to_dict() for name, table in self.tables.items()}
        }
        
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load database from file."""
        if not self.db_file or not os.path.exists(self.db_file):
            return
        
        # Check if file is empty
        if os.path.getsize(self.db_file) == 0:
            return
        
        with open(self.db_file, 'r') as f:
            data = json.load(f)
        
        self.tables = {}
        for name, table_data in data.get('tables', {}).items():
            self.tables[name] = Table.from_dict(table_data)
