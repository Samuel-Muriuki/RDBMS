"""
Unit tests for storage engine.
"""

import pytest
import os
import tempfile
from simpledb.storage import Database, Table
from simpledb.exceptions import (
    PrimaryKeyViolation, UniqueConstraintViolation,
    NotNullViolation, TableNotFoundError
)


class TestTable:
    """Test Table functionality."""
    
    def test_create_table(self):
        """Test table creation."""
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'name', 'type': 'VARCHAR', 'length': 50}
        ]
        table = Table('users', columns)
        
        assert table.name == 'users'
        assert len(table.columns) == 2
        assert table.primary_key == 'id'
    
    def test_insert_row(self):
        """Test row insertion."""
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'name', 'type': 'VARCHAR', 'length': 50}
        ]
        table = Table('users', columns)
        
        table.insert_row({'id': 1, 'name': 'Alice'})
        assert len(table.rows) == 1
        assert table.rows[0]['name'] == 'Alice'
    
    def test_primary_key_violation(self):
        """Test primary key constraint."""
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'name', 'type': 'VARCHAR', 'length': 50}
        ]
        table = Table('users', columns)
        
        table.insert_row({'id': 1, 'name': 'Alice'})
        
        with pytest.raises(PrimaryKeyViolation):
            table.insert_row({'id': 1, 'name': 'Bob'})
    
    def test_unique_constraint(self):
        """Test UNIQUE constraint."""
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'email', 'type': 'VARCHAR', 'length': 100, 'constraints': ['UNIQUE']}
        ]
        table = Table('users', columns)
        
        table.insert_row({'id': 1, 'email': 'alice@example.com'})
        
        with pytest.raises(UniqueConstraintViolation):
            table.insert_row({'id': 2, 'email': 'alice@example.com'})
    
    def test_not_null_constraint(self):
        """Test NOT NULL constraint."""
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'name', 'type': 'VARCHAR', 'length': 50, 'constraints': ['NOT NULL']}
        ]
        table = Table('users', columns)
        
        with pytest.raises(NotNullViolation):
            table.insert_row({'id': 1, 'name': None})
    
    def test_update_row(self):
        """Test row update."""
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'name', 'type': 'VARCHAR', 'length': 50}
        ]
        table = Table('users', columns)
        
        table.insert_row({'id': 1, 'name': 'Alice'})
        table.update_row(0, {'name': 'Alice Smith'})
        
        assert table.rows[0]['name'] == 'Alice Smith'
    
    def test_delete_row(self):
        """Test row deletion."""
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'name', 'type': 'VARCHAR', 'length': 50}
        ]
        table = Table('users', columns)
        
        table.insert_row({'id': 1, 'name': 'Alice'})
        table.delete_row(0)
        
        assert table.rows[0] is None
    
    def test_find_rows(self):
        """Test finding rows with conditions."""
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'age', 'type': 'INT'}
        ]
        table = Table('users', columns)
        
        table.insert_row({'id': 1, 'age': 25})
        table.insert_row({'id': 2, 'age': 30})
        table.insert_row({'id': 3, 'age': 25})
        
        conditions = [{'column': 'age', 'operator': '=', 'value': 25}]
        indexes = table.find_rows(conditions)
        
        assert len(indexes) == 2


class TestDatabase:
    """Test Database functionality."""
    
    def test_create_table(self):
        """Test creating a table in database."""
        db = Database()
        columns = [
            {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
            {'name': 'name', 'type': 'VARCHAR', 'length': 50}
        ]
        
        db.create_table('users', columns)
        assert 'users' in db.tables
    
    def test_drop_table(self):
        """Test dropping a table."""
        db = Database()
        columns = [{'name': 'id', 'type': 'INT'}]
        
        db.create_table('users', columns)
        db.drop_table('users')
        
        assert 'users' not in db.tables
    
    def test_get_table(self):
        """Test getting a table."""
        db = Database()
        columns = [{'name': 'id', 'type': 'INT'}]
        
        db.create_table('users', columns)
        table = db.get_table('users')
        
        assert table.name == 'users'
    
    def test_get_nonexistent_table(self):
        """Test getting a non-existent table raises error."""
        db = Database()
        
        with pytest.raises(TableNotFoundError):
            db.get_table('nonexistent')
    
    def test_persistence(self):
        """Test saving and loading database."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            db_file = f.name
        
        try:
            # Create and save database
            db = Database(db_file)
            columns = [
                {'name': 'id', 'type': 'INT', 'constraints': ['PRIMARY KEY']},
                {'name': 'name', 'type': 'VARCHAR', 'length': 50}
            ]
            db.create_table('users', columns)
            db.get_table('users').insert_row({'id': 1, 'name': 'Alice'})
            db.save()
            
            # Load database
            db2 = Database(db_file)
            table = db2.get_table('users')
            
            assert len(table.rows) == 1
            assert table.rows[0]['name'] == 'Alice'
        
        finally:
            if os.path.exists(db_file):
                os.unlink(db_file)
