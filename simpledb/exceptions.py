"""
Custom exceptions for SimpleDB.
"""


class SimpleDBException(Exception):
    """Base exception for all SimpleDB errors."""
    pass


class ParseError(SimpleDBException):
    """Raised when SQL parsing fails."""
    pass


class TableNotFoundError(SimpleDBException):
    """Raised when attempting to access a non-existent table."""
    pass


class PrimaryKeyViolation(SimpleDBException):
    """Raised when attempting to insert a duplicate primary key."""
    pass


class UniqueConstraintViolation(SimpleDBException):
    """Raised when attempting to insert a duplicate value in a UNIQUE column."""
    pass


class NotNullViolation(SimpleDBException):
    """Raised when attempting to insert NULL into a NOT NULL column."""
    pass


class DataTypeError(SimpleDBException):
    """Raised when a value doesn't match the expected data type."""
    pass


class ColumnNotFoundError(SimpleDBException):
    """Raised when referencing a non-existent column."""
    pass
