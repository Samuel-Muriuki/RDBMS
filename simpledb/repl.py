"""
Interactive REPL for SimpleDB.

Provides a command-line interface for executing SQL queries.
"""

import sys
import os
from .storage import Database
from .executor import QueryExecutor
from .exceptions import SimpleDBException


class REPL:
    """Interactive Read-Eval-Print Loop for SimpleDB."""
    
    def __init__(self, db_file: str = 'simpledb.json'):
        self.db = Database(db_file)
        self.executor = QueryExecutor(self.db)
        self.running = True
    
    def print_table(self, columns: list, rows: list):
        """Print results in a formatted table."""
        if not rows:
            print("0 row(s) selected.")
            return
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            col_widths[col] = len(str(col))
        
        for row in rows:
            for col in columns:
                value = row.get(col, '')
                col_widths[col] = max(col_widths[col], len(str(value)))
        
        # Print header
        header = '+' + '+'.join('-' * (col_widths[col] + 2) for col in columns) + '+'
        print(header)
        
        col_row = '|' + '|'.join(f" {col:<{col_widths[col]}} " for col in columns) + '|'
        print(col_row)
        print(header)
        
        # Print rows
        for row in rows:
            values = []
            for col in columns:
                value = row.get(col, '')
                if value is None:
                    value = 'NULL'
                values.append(f" {str(value):<{col_widths[col]}} ")
            print('|' + '|'.join(values) + '|')
        
        print(header)
        print(f"{len(rows)} row(s) selected.")
    
    def execute_special_command(self, command: str) -> bool:
        """Execute special REPL commands. Returns True if command was handled."""
        command = command.strip()
        
        if command == '.exit' or command == '.quit':
            print("Goodbye!")
            self.running = False
            return True
        
        elif command == '.tables':
            tables = self.db.list_tables()
            if tables:
                print("Tables:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("No tables found.")
            return True
        
        elif command.startswith('.schema'):
            parts = command.split()
            if len(parts) < 2:
                print("Usage: .schema <table_name>")
                return True
            
            table_name = parts[1]
            try:
                table = self.db.get_table(table_name)
                print(f"\nTable: {table.name}")
                print("Columns:")
                for col in table.columns:
                    col_def = f"  - {col['name']} {col['type']}"
                    if col['type'] == 'VARCHAR':
                        col_def += f"({col.get('length', 255)})"
                    if 'constraints' in col:
                        col_def += f" [{', '.join(col['constraints'])}]"
                    print(col_def)
            except SimpleDBException as e:
                print(f"Error: {e}")
            return True
        
        elif command == '.help':
            print("\nSimpleDB REPL Commands:")
            print("  .exit, .quit     - Exit the REPL")
            print("  .tables          - List all tables")
            print("  .schema <table>  - Show table schema")
            print("  .help            - Show this help message")
            print("\nSQL Commands:")
            print("  CREATE TABLE ... - Create a new table")
            print("  DROP TABLE ...   - Drop a table")
            print("  INSERT INTO ...  - Insert a row")
            print("  SELECT ...       - Query data")
            print("  UPDATE ...       - Update rows")
            print("  DELETE FROM ...  - Delete rows")
            print("\nEnd SQL statements with a semicolon (;)")
            return True
        
        return False
    
    def run(self):
        """Start the REPL."""
        print("=" * 60)
        print("SimpleDB - Interactive SQL Shell")
        print("=" * 60)
        print("Type .help for help, .exit to quit")
        print()
        
        buffer = []
        
        while self.running:
            try:
                # Prompt
                if buffer:
                    prompt = "    ...> "
                else:
                    prompt = "SimpleDB> "
                
                line = input(prompt).strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Handle special commands
                if line.startswith('.'):
                    if buffer:
                        print("Error: Cannot use special commands in multi-line mode")
                        buffer = []
                        continue
                    self.execute_special_command(line)
                    continue
                
                # Add to buffer
                buffer.append(line)
                
                # Check if statement is complete (ends with semicolon)
                if line.endswith(';'):
                    sql = ' '.join(buffer)
                    buffer = []
                    
                    # Execute SQL
                    result = self.executor.execute(sql)
                    
                    if result['success']:
                        if 'rows' in result:
                            # SELECT query
                            self.print_table(result['columns'], result['rows'])
                        else:
                            # Other queries
                            print(result.get('message', 'Success'))
                    else:
                        print(f"Error: {result['error']}")
                    
                    print()
            
            except KeyboardInterrupt:
                print("\nInterrupted. Type .exit to quit.")
                buffer = []
                print()
            
            except EOFError:
                print("\nGoodbye!")
                break
            
            except Exception as e:
                print(f"Unexpected error: {e}")
                buffer = []


def main():
    """Entry point for REPL."""
    db_file = 'simpledb.json'
    if len(sys.argv) > 1:
        db_file = sys.argv[1]
    
    repl = REPL(db_file)
    repl.run()


if __name__ == '__main__':
    main()
