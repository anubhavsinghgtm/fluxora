


class AppException(Exception):
    """Base class for application exceptions."""
    pass


class InvalidSQLGeneratedException(AppException):
    """LLM returned something that isn't a valid SELECT query."""
    pass


class LLMQuotaExceededException(AppException):
    """LLM quota exceeded."""
    pass

class LLMException(AppException):
    """General LLM exception."""
    pass

class DatabaseQueryException(AppException):
    """Exception raised for errors during database query execution."""
    pass


class SchemaFetchException(AppException):
    """Exception raised for errors during schema fetching from the database."""
    pass
    