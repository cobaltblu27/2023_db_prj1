class SqlException(Exception):
    message: str = "SQL Error!"


class SyntaxError(SqlException):
    message = "Syntax Error"


class CreateTableSuccess(SqlException):
    pass


class DuplicateColumnDefError(SqlException):
    pass


class DuplicatePrimaryKeyDefError(SqlException):
    pass


class ReferenceTypeError(SqlException):
    pass


class ReferenceNonPrimaryKeyError(SqlException):
    pass


class ReferenceColumnExistenceError(SqlException):
    pass


class ReferenceTableExistenceError(SqlException):
    pass


class NonExistingColumnDefError(SqlException):
    pass


class TableExistenceError(SqlException):
    pass


class CharLengthError(SqlException):
    pass


class DropSuccess(SqlException):
    pass


class NoSuchTable(SqlException):
    message = "No such table"


class DropReferencedTableError(SqlException):
    pass


class InsertResult(SqlException):
    pass


class SelectTableExistenceError(SqlException):
    pass
