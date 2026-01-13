"""
Integration tests for query executor.
"""

import pytest
import os
import tempfile
from simpledb.storage import Database
from simpledb.executor import QueryExecutor


class TestExecutor:
    """Test query executor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.db = Database()
        self.executor = QueryExecutor(self.db)
    
    def test_create_table(self):
        """Test CREATE TABLE execution."""
        sql = "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));"
        result = self.executor.execute(sql)
        
        assert result['success'] is True
        assert 'users' in self.db.tables
    
    def test_insert(self):
        """Test INSERT execution."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        result = self.executor.execute("INSERT INTO users VALUES (1, 'Alice');")
        
        assert result['success'] is True
        table = self.db.get_table('users')
        assert len(table.rows) == 1
    
    def test_select_all(self):
        """Test SELECT * execution."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        self.executor.execute("INSERT INTO users VALUES (1, 'Alice');")
        self.executor.execute("INSERT INTO users VALUES (2, 'Bob');")
        
        result = self.executor.execute("SELECT * FROM users;")
        
        assert result['success'] is True
        assert len(result['rows']) == 2
        assert result['columns'] == ['id', 'name']
    
    def test_select_with_where(self):
        """Test SELECT with WHERE clause."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        self.executor.execute("INSERT INTO users VALUES (1, 'Alice');")
        self.executor.execute("INSERT INTO users VALUES (2, 'Bob');")
        
        result = self.executor.execute("SELECT * FROM users WHERE id = 1;")
        
        assert result['success'] is True
        assert len(result['rows']) == 1
        assert result['rows'][0]['name'] == 'Alice'
    
    def test_select_with_order_by(self):
        """Test SELECT with ORDER BY."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        self.executor.execute("INSERT INTO users VALUES (1, 'Charlie');")
        self.executor.execute("INSERT INTO users VALUES (2, 'Alice');")
        self.executor.execute("INSERT INTO users VALUES (3, 'Bob');")
        
        result = self.executor.execute("SELECT * FROM users ORDER BY name ASC;")
        
        assert result['success'] is True
        assert result['rows'][0]['name'] == 'Alice'
        assert result['rows'][1]['name'] == 'Bob'
        assert result['rows'][2]['name'] == 'Charlie'
    
    def test_select_with_limit(self):
        """Test SELECT with LIMIT."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        self.executor.execute("INSERT INTO users VALUES (1, 'Alice');")
        self.executor.execute("INSERT INTO users VALUES (2, 'Bob');")
        self.executor.execute("INSERT INTO users VALUES (3, 'Charlie');")
        
        result = self.executor.execute("SELECT * FROM users LIMIT 2;")
        
        assert result['success'] is True
        assert len(result['rows']) == 2
    
    def test_update(self):
        """Test UPDATE execution."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        self.executor.execute("INSERT INTO users VALUES (1, 'Alice');")
        
        result = self.executor.execute("UPDATE users SET name = 'Alice Smith' WHERE id = 1;")
        
        assert result['success'] is True
        table = self.db.get_table('users')
        assert table.rows[0]['name'] == 'Alice Smith'
    
    def test_delete(self):
        """Test DELETE execution."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        self.executor.execute("INSERT INTO users VALUES (1, 'Alice');")
        self.executor.execute("INSERT INTO users VALUES (2, 'Bob');")
        
        result = self.executor.execute("DELETE FROM users WHERE id = 1;")
        
        assert result['success'] is True
        table = self.db.get_table('users')
        assert table.rows[0] is None
        assert table.rows[1] is not None
    
    def test_drop_table(self):
        """Test DROP TABLE execution."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        result = self.executor.execute("DROP TABLE users;")
        
        assert result['success'] is True
        assert 'users' not in self.db.tables
    
    def test_constraint_violation(self):
        """Test that constraint violations are handled."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50));")
        self.executor.execute("INSERT INTO users VALUES (1, 'Alice');")
        
        result = self.executor.execute("INSERT INTO users VALUES (1, 'Bob');")
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_complex_query(self):
        """Test complex query with multiple clauses."""
        self.executor.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50), age INT);")
        self.executor.execute("INSERT INTO users VALUES (1, 'Alice', 25);")
        self.executor.execute("INSERT INTO users VALUES (2, 'Bob', 30);")
        self.executor.execute("INSERT INTO users VALUES (3, 'Charlie', 25);")
        self.executor.execute("INSERT INTO users VALUES (4, 'David', 35);")
        
        result = self.executor.execute("SELECT name FROM users WHERE age >= 25 ORDER BY name ASC LIMIT 3;")
        
        assert result['success'] is True
        assert len(result['rows']) == 3
        assert result['rows'][0]['name'] == 'Alice'
