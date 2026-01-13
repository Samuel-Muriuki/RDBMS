"""
Query executor for SimpleDB.

Executes parsed SQL commands on the storage engine.
"""

from typing import Dict, Any, List, Optional
from .parser import Parser
from .storage import Database
from .exceptions import SimpleDBException


class QueryExecutor:
    """Executes SQL queries on a database."""
    
    def __init__(self, database: Database):
        self.db = database
        self.parser = Parser()
    
    def execute(self, sql: str) -> Dict[str, Any]:
        """Execute a SQL statement and return results."""
        try:
            # Parse SQL
            command = self.parser.parse(sql)
            
            # Execute based on command type
            cmd_type = command['command']
            
            if cmd_type == 'CREATE':
                return self._execute_create(command)
            elif cmd_type == 'DROP':
                return self._execute_drop(command)
            elif cmd_type == 'INSERT':
                return self._execute_insert(command)
            elif cmd_type == 'SELECT':
                return self._execute_select(command)
            elif cmd_type == 'UPDATE':
                return self._execute_update(command)
            elif cmd_type == 'DELETE':
                return self._execute_delete(command)
            else:
                return {'success': False, 'error': f"Unknown command: {cmd_type}"}
        
        except SimpleDBException as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f"Unexpected error: {str(e)}"}
    
    def _execute_create(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CREATE TABLE command."""
        table_name = command['table']
        columns = command['columns']
        
        self.db.create_table(table_name, columns)
        self.db.save()
        
        return {
            'success': True,
            'message': f"Table '{table_name}' created successfully"
        }
    
    def _execute_drop(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DROP TABLE command."""
        table_name = command['table']
        
        self.db.drop_table(table_name)
        self.db.save()
        
        return {
            'success': True,
            'message': f"Table '{table_name}' dropped successfully"
        }
    
    def _execute_insert(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute INSERT command."""
        table_name = command['table']
        values = command['values']
        columns = command.get('columns')
        
        table = self.db.get_table(table_name)
        
        # Build row dictionary
        if columns:
            # Specific columns provided
            if len(columns) != len(values):
                return {'success': False, 'error': 'Column count does not match value count'}
            row = {col: val for col, val in zip(columns, values)}
        else:
            # Use all columns in order
            if len(table.columns) != len(values):
                return {'success': False, 'error': f'Expected {len(table.columns)} values, got {len(values)}'}
            row = {col['name']: val for col, val in zip(table.columns, values)}
        
        table.insert_row(row)
        self.db.save()
        
        return {
            'success': True,
            'message': '1 row inserted'
        }
    
    def _execute_select(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SELECT command."""
        table_name = command['table']
        columns = command['columns']
        where = command.get('where')
        order_by = command.get('order_by')
        limit = command.get('limit')
        
        table = self.db.get_table(table_name)
        
        # Find matching rows
        conditions = where['conditions'] if where else None
        row_indexes = table.find_rows(conditions)
        
        # Get rows
        rows = [table.rows[i] for i in row_indexes]
        
        # Apply ORDER BY
        if order_by:
            col_name = order_by['column']
            reverse = order_by['direction'] == 'DESC'
            rows.sort(key=lambda r: r.get(col_name) if r.get(col_name) is not None else '', reverse=reverse)
        
        # Apply LIMIT
        if limit:
            rows = rows[:limit]
        
        # Select columns
        if columns == ['*']:
            result_columns = [col['name'] for col in table.columns]
            result_rows = rows
        else:
            result_columns = columns
            result_rows = [{col: row.get(col) for col in columns} for row in rows]
        
        return {
            'success': True,
            'columns': result_columns,
            'rows': result_rows,
            'count': len(result_rows)
        }
    
    def _execute_update(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute UPDATE command."""
        table_name = command['table']
        updates = command['updates']
        where = command.get('where')
        
        table = self.db.get_table(table_name)
        
        # Find matching rows
        conditions = where['conditions'] if where else None
        row_indexes = table.find_rows(conditions)
        
        # Update rows
        for index in row_indexes:
            table.update_row(index, updates)
        
        self.db.save()
        
        return {
            'success': True,
            'message': f"{len(row_indexes)} row(s) updated"
        }
    
    def _execute_delete(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DELETE command."""
        table_name = command['table']
        where = command.get('where')
        
        table = self.db.get_table(table_name)
        
        # Find matching rows
        conditions = where['conditions'] if where else None
        row_indexes = table.find_rows(conditions)
        
        # Delete rows (in reverse order to maintain indexes)
        for index in sorted(row_indexes, reverse=True):
            table.delete_row(index)
        
        self.db.save()
        
        return {
            'success': True,
            'message': f"{len(row_indexes)} row(s) deleted"
        }
