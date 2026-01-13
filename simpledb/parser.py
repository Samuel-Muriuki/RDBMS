"""
SQL Parser for SimpleDB.

Tokenizes and parses SQL commands into structured dictionaries.
"""

import re
from typing import List, Dict, Any, Optional
from .exceptions import ParseError


class Token:
    """Represents a single token in SQL."""
    
    def __init__(self, type_: str, value: Any):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


class Tokenizer:
    """Tokenizes SQL strings into a list of tokens."""
    
    # SQL keywords
    KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET',
        'DELETE', 'CREATE', 'TABLE', 'DROP', 'PRIMARY', 'KEY', 'UNIQUE', 'NOT',
        'NULL', 'INT', 'VARCHAR', 'BOOLEAN', 'ORDER', 'BY', 'LIMIT', 'ASC', 'DESC',
        'AND', 'OR', 'INNER', 'JOIN', 'ON', 'TRUE', 'FALSE', 'IF', 'EXISTS', 'AS'
    }
    
    # Operators
    OPERATORS = {'=', '!=', '<', '<=', '>', '>=', ',', '(', ')', ';', '*'}
    
    def tokenize(self, sql: str) -> List[Token]:
        """Convert SQL string into list of tokens."""
        tokens = []
        i = 0
        sql = sql.strip()
        
        while i < len(sql):
            # Skip whitespace
            if sql[i].isspace():
                i += 1
                continue
            
            # Handle strings (single or double quotes)
            if sql[i] in ('"', "'"):
                quote = sql[i]
                i += 1
                start = i
                while i < len(sql) and sql[i] != quote:
                    if sql[i] == '\\' and i + 1 < len(sql):
                        i += 2
                    else:
                        i += 1
                if i >= len(sql):
                    raise ParseError(f"Unterminated string starting at position {start}")
                tokens.append(Token('STRING', sql[start:i]))
                i += 1
                continue
            
            # Handle numbers
            if sql[i].isdigit() or (sql[i] == '-' and i + 1 < len(sql) and sql[i + 1].isdigit()):
                start = i
                if sql[i] == '-':
                    i += 1
                while i < len(sql) and (sql[i].isdigit() or sql[i] == '.'):
                    i += 1
                num_str = sql[start:i]
                if '.' in num_str:
                    tokens.append(Token('NUMBER', float(num_str)))
                else:
                    tokens.append(Token('NUMBER', int(num_str)))
                continue
            
            # Handle two-character operators
            if i + 1 < len(sql) and sql[i:i+2] in ('!=', '<=', '>='):
                tokens.append(Token('OPERATOR', sql[i:i+2]))
                i += 2
                continue
            
            # Handle single-character operators
            if sql[i] in self.OPERATORS:
                tokens.append(Token('OPERATOR', sql[i]))
                i += 1
                continue
            
            # Handle identifiers and keywords
            if sql[i].isalpha() or sql[i] == '_':
                start = i
                while i < len(sql) and (sql[i].isalnum() or sql[i] in ('_', '.')):
                    i += 1
                word = sql[start:i]
                word_upper = word.upper()
                
                if word_upper in self.KEYWORDS:
                    tokens.append(Token('KEYWORD', word_upper))
                elif word_upper == 'TRUE':
                    tokens.append(Token('BOOLEAN', True))
                elif word_upper == 'FALSE':
                    tokens.append(Token('BOOLEAN', False))
                else:
                    tokens.append(Token('IDENTIFIER', word))
                continue
            
            raise ParseError(f"Unexpected character '{sql[i]}' at position {i}")
        
        return tokens


class Parser:
    """Parses tokens into structured command dictionaries."""
    
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.tokens = []
        self.pos = 0
    
    def parse(self, sql: str) -> Dict[str, Any]:
        """Parse SQL string into command dictionary."""
        self.tokens = self.tokenizer.tokenize(sql)
        self.pos = 0
        
        if not self.tokens:
            raise ParseError("Empty SQL statement")
        
        # Remove trailing semicolon if present
        if self.tokens and self.tokens[-1].type == 'OPERATOR' and self.tokens[-1].value == ';':
            self.tokens.pop()
        
        if not self.tokens:
            raise ParseError("Empty SQL statement")
        
        first_token = self.current()
        if first_token.type != 'KEYWORD':
            raise ParseError(f"Expected keyword, got {first_token.type}")
        
        command = first_token.value
        
        if command == 'CREATE':
            return self.parse_create()
        elif command == 'DROP':
            return self.parse_drop()
        elif command == 'INSERT':
            return self.parse_insert()
        elif command == 'SELECT':
            return self.parse_select()
        elif command == 'UPDATE':
            return self.parse_update()
        elif command == 'DELETE':
            return self.parse_delete()
        else:
            raise ParseError(f"Unknown command: {command}")
    
    def current(self) -> Optional[Token]:
        """Get current token without advancing."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def advance(self) -> Optional[Token]:
        """Get current token and advance position."""
        token = self.current()
        self.pos += 1
        return token
    
    def expect(self, type_: str, value: Any = None) -> Token:
        """Expect a specific token type and optionally value."""
        token = self.current()
        if not token:
            raise ParseError(f"Expected {type_} but reached end of statement")
        if token.type != type_:
            raise ParseError(f"Expected {type_}, got {token.type}")
        if value is not None and token.value != value:
            raise ParseError(f"Expected {value}, got {token.value}")
        return self.advance()
    
    def parse_create(self) -> Dict[str, Any]:
        """Parse CREATE TABLE statement."""
        self.expect('KEYWORD', 'CREATE')
        self.expect('KEYWORD', 'TABLE')
        
        if_not_exists = False
        if self.current() and self.current().value == 'IF':
            self.advance()
            self.expect('KEYWORD', 'NOT')
            self.expect('KEYWORD', 'EXISTS')
            if_not_exists = True
            
        table_name = self.expect('IDENTIFIER').value
        
        self.expect('OPERATOR', '(')
        
        columns = []
        while True:
            col_name = self.expect('IDENTIFIER').value
            col_type_token = self.expect('KEYWORD')
            col_type = col_type_token.value
            
            col_def = {'name': col_name, 'type': col_type}
            
            # Handle VARCHAR(n)
            if col_type == 'VARCHAR':
                self.expect('OPERATOR', '(')
                length = self.expect('NUMBER').value
                self.expect('OPERATOR', ')')
                col_def['length'] = length
            
            # Handle constraints
            constraints = []
            while self.current() and self.current().type == 'KEYWORD':
                keyword = self.current().value
                if keyword == 'PRIMARY':
                    self.advance()
                    self.expect('KEYWORD', 'KEY')
                    constraints.append('PRIMARY KEY')
                elif keyword == 'UNIQUE':
                    self.advance()
                    constraints.append('UNIQUE')
                elif keyword == 'NOT':
                    self.advance()
                    self.expect('KEYWORD', 'NULL')
                    constraints.append('NOT NULL')
                else:
                    break
            
            if constraints:
                col_def['constraints'] = constraints
            
            columns.append(col_def)
            
            if self.current() and self.current().value == ',':
                self.advance()
            else:
                break
        
        self.expect('OPERATOR', ')')
        
        return {
            'command': 'CREATE',
            'table': table_name,
            'columns': columns,
            'if_not_exists': if_not_exists
        }
    
    def parse_drop(self) -> Dict[str, Any]:
        """Parse DROP TABLE statement."""
        self.expect('KEYWORD', 'DROP')
        self.expect('KEYWORD', 'TABLE')
        table_name = self.expect('IDENTIFIER').value
        
        return {
            'command': 'DROP',
            'table': table_name
        }
    
    def parse_insert(self) -> Dict[str, Any]:
        """Parse INSERT INTO statement."""
        self.expect('KEYWORD', 'INSERT')
        self.expect('KEYWORD', 'INTO')
        table_name = self.expect('IDENTIFIER').value
        
        columns = None
        if self.current() and self.current().value == '(':
            self.advance()
            columns = []
            while True:
                columns.append(self.expect('IDENTIFIER').value)
                if self.current() and self.current().value == ',':
                    self.advance()
                else:
                    break
            self.expect('OPERATOR', ')')
        
        self.expect('KEYWORD', 'VALUES')
        self.expect('OPERATOR', '(')
        
        values = []
        while True:
            token = self.current()
            if token.type in ('STRING', 'NUMBER', 'BOOLEAN'):
                values.append(self.advance().value)
            elif token.type == 'KEYWORD' and token.value == 'NULL':
                self.advance()
                values.append(None)
            else:
                raise ParseError(f"Expected value, got {token.type}")
            
            if self.current() and self.current().value == ',':
                self.advance()
            else:
                break
        
        self.expect('OPERATOR', ')')
        
        result = {
            'command': 'INSERT',
            'table': table_name,
            'values': values
        }
        
        if columns:
            result['columns'] = columns
        
        return result
    
    def parse_select(self) -> Dict[str, Any]:
        """Parse SELECT statement."""
        self.expect('KEYWORD', 'SELECT')
        
        # Parse columns
        columns = []
        while True:
            # Check if we've reached FROM
            if self.current() and self.current().type == 'KEYWORD' and self.current().value == 'FROM':
                break
                
            if self.current() and self.current().value == '*':
                self.advance()
                columns.append('*')
            elif self.current() and self.current().type == 'IDENTIFIER' and self.current().value.upper() == 'COUNT':
                self.advance() # COUNT
                self.expect('OPERATOR', '(')
                self.expect('OPERATOR', '*')
                self.expect('OPERATOR', ')')
                # Handle AS alias
                alias = 'count'
                if self.current() and self.current().type == 'KEYWORD' and self.current().value == 'AS':
                    self.advance()
                    alias = self.expect('IDENTIFIER').value
                columns.append(f'COUNT(*) AS {alias}')
            elif self.current() and self.current().type == 'IDENTIFIER':
                col_name = self.advance().value
                # Handle AS alias
                if self.current() and self.current().type == 'KEYWORD' and self.current().value == 'AS':
                    self.advance()
                    alias = self.expect('IDENTIFIER').value
                    columns.append(f"{col_name} AS {alias}")
                else:
                    columns.append(col_name)
            else:
                current_val = self.current().value if self.current() else 'EOF'
                raise ParseError(f"Expected column or FROM, got {current_val}")
            
            if self.current() and self.current().value == ',':
                self.advance()
            elif self.current() and self.current().type == 'KEYWORD' and self.current().value == 'FROM':
                break
            else:
                # If next isn't a comma or FROM, we might have an issue, 
                # but often it's just the end of the col list before FROM
                break
        
        self.expect('KEYWORD', 'FROM')
        table_name = self.expect('IDENTIFIER').value
        
        result = {
            'command': 'SELECT',
            'columns': columns,
            'table': table_name
        }
        
        # Parse optional JOIN
        if self.current() and self.current().type == 'KEYWORD' and self.current().value in ('INNER', 'JOIN'):
            if self.current().value == 'INNER':
                self.advance()
                self.expect('KEYWORD', 'JOIN')
            else:
                self.advance() # JOIN
                
            join_table = self.expect('IDENTIFIER').value
            self.expect('KEYWORD', 'ON')
            
            left_col = self.expect('IDENTIFIER').value
            self.expect('OPERATOR', '=')
            right_col = self.expect('IDENTIFIER').value
            
            result['join'] = {
                'table': join_table,
                'on': {
                    'left': left_col,
                    'right': right_col
                }
            }
        
        # Parse optional WHERE
        if self.current() and self.current().value == 'WHERE':
            self.advance()
            result['where'] = self.parse_where()
        
        # Parse optional ORDER BY
        if self.current() and self.current().value == 'ORDER':
            self.advance()
            self.expect('KEYWORD', 'BY')
            order_col = self.expect('IDENTIFIER').value
            direction = 'ASC'
            if self.current() and self.current().type == 'KEYWORD' and self.current().value in ('ASC', 'DESC'):
                direction = self.advance().value
            result['order_by'] = {'column': order_col, 'direction': direction}
        
        # Parse optional LIMIT
        if self.current() and self.current().value == 'LIMIT':
            self.advance()
            result['limit'] = self.expect('NUMBER').value
        
        return result
    
    def parse_where(self) -> Dict[str, Any]:
        """Parse WHERE clause."""
        conditions = []
        
        while True:
            column = self.expect('IDENTIFIER').value
            operator = self.expect('OPERATOR').value
            
            value_token = self.current()
            if value_token.type in ('STRING', 'NUMBER', 'BOOLEAN'):
                value = self.advance().value
            elif value_token.type == 'KEYWORD' and value_token.value == 'NULL':
                self.advance()
                value = None
            else:
                raise ParseError(f"Expected value in WHERE clause, got {value_token.type}")
            
            conditions.append({
                'column': column,
                'operator': operator,
                'value': value
            })
            
            if self.current() and self.current().type == 'KEYWORD' and self.current().value in ('AND', 'OR'):
                logic = self.advance().value
                conditions.append({'logic': logic})
            else:
                break
        
        return {'conditions': conditions}
    
    def parse_update(self) -> Dict[str, Any]:
        """Parse UPDATE statement."""
        self.expect('KEYWORD', 'UPDATE')
        table_name = self.expect('IDENTIFIER').value
        self.expect('KEYWORD', 'SET')
        
        updates = {}
        while True:
            column = self.expect('IDENTIFIER').value
            self.expect('OPERATOR', '=')
            
            value_token = self.current()
            if value_token.type in ('STRING', 'NUMBER', 'BOOLEAN'):
                value = self.advance().value
            elif value_token.type == 'KEYWORD' and value_token.value == 'NULL':
                self.advance()
                value = None
            else:
                raise ParseError(f"Expected value in SET clause, got {value_token.type}")
            
            updates[column] = value
            
            if self.current() and self.current().value == ',':
                self.advance()
            else:
                break
        
        result = {
            'command': 'UPDATE',
            'table': table_name,
            'updates': updates
        }
        
        if self.current() and self.current().value == 'WHERE':
            self.advance()
            result['where'] = self.parse_where()
        
        return result
    
    def parse_delete(self) -> Dict[str, Any]:
        """Parse DELETE statement."""
        self.expect('KEYWORD', 'DELETE')
        self.expect('KEYWORD', 'FROM')
        table_name = self.expect('IDENTIFIER').value
        
        result = {
            'command': 'DELETE',
            'table': table_name
        }
        
        if self.current() and self.current().value == 'WHERE':
            self.advance()
            result['where'] = self.parse_where()
        
        return result
