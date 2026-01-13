"""
Unit tests for SQL parser.
"""

import pytest
from simpledb.parser import Parser
from simpledb.exceptions import ParseError


class TestParser:
    """Test SQL parser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = Parser()
    
    def test_create_table(self):
        """Test CREATE TABLE parsing."""
        sql = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50) NOT NULL);"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'CREATE'
        assert result['table'] == 'users'
        assert len(result['columns']) == 2
        assert result['columns'][0]['name'] == 'id'
        assert result['columns'][0]['type'] == 'INT'
        assert 'PRIMARY KEY' in result['columns'][0]['constraints']
    
    def test_insert(self):
        """Test INSERT parsing."""
        sql = "INSERT INTO users VALUES (1, 'Alice');"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'INSERT'
        assert result['table'] == 'users'
        assert result['values'] == [1, 'Alice']
    
    def test_insert_with_columns(self):
        """Test INSERT with column specification."""
        sql = "INSERT INTO users (name, id) VALUES ('Bob', 2);"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'INSERT'
        assert result['columns'] == ['name', 'id']
        assert result['values'] == ['Bob', 2]
    
    def test_select_all(self):
        """Test SELECT * parsing."""
        sql = "SELECT * FROM users;"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'SELECT'
        assert result['columns'] == ['*']
        assert result['table'] == 'users'
    
    def test_select_with_where(self):
        """Test SELECT with WHERE clause."""
        sql = "SELECT name FROM users WHERE id = 1;"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'SELECT'
        assert result['columns'] == ['name']
        assert 'where' in result
        assert result['where']['conditions'][0]['column'] == 'id'
        assert result['where']['conditions'][0]['operator'] == '='
        assert result['where']['conditions'][0]['value'] == 1
    
    def test_select_with_order_by(self):
        """Test SELECT with ORDER BY."""
        sql = "SELECT * FROM users ORDER BY name DESC;"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'SELECT'
        assert 'order_by' in result
        assert result['order_by']['column'] == 'name'
        assert result['order_by']['direction'] == 'DESC'
    
    def test_select_with_limit(self):
        """Test SELECT with LIMIT."""
        sql = "SELECT * FROM users LIMIT 10;"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'SELECT'
        assert result['limit'] == 10
    
    def test_update(self):
        """Test UPDATE parsing."""
        sql = "UPDATE users SET name = 'Charlie' WHERE id = 1;"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'UPDATE'
        assert result['table'] == 'users'
        assert result['updates'] == {'name': 'Charlie'}
        assert result['where']['conditions'][0]['column'] == 'id'
    
    def test_delete(self):
        """Test DELETE parsing."""
        sql = "DELETE FROM users WHERE id = 1;"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'DELETE'
        assert result['table'] == 'users'
        assert result['where']['conditions'][0]['column'] == 'id'
    
    def test_drop_table(self):
        """Test DROP TABLE parsing."""
        sql = "DROP TABLE users;"
        result = self.parser.parse(sql)
        
        assert result['command'] == 'DROP'
        assert result['table'] == 'users'
    
    def test_invalid_sql(self):
        """Test that invalid SQL raises ParseError."""
        with pytest.raises(ParseError):
            self.parser.parse("INVALID SQL STATEMENT;")
    
    def test_empty_sql(self):
        """Test that empty SQL raises ParseError."""
        with pytest.raises(ParseError):
            self.parser.parse("")
