class SqlException(Exception):
    message: str = "SQL Error!"


class SyntaxError(SqlException):
    message = "Syntax Error"


class DuplicateColumnDefError(SqlException):
    message = "Create table has failed: column definition is duplicated"


class DuplicatePrimaryKeyDefError(SqlException):
    message = "Create table has failed: primary key definition is duplicated"


class ReferenceTypeError(SqlException):
    message = "Create table has failed: foreign key references wrong type"


class ReferenceNonPrimaryKeyError(SqlException): 
    message = "Create table has failed: foreign key references non primary key column"


class ReferenceColumnExistenceError(SqlException):
    message = "Create table has failed: foreign key referneces non existing column"
    pass


class ReferenceTableExistenceError(SqlException):
    message = "Create table has failed: foreign key referneces non existing table"


class NonExistingColumnDefError(SqlException):
    def __init__(self, col_name: str) -> None:
        super().__init__()
        self.message = "Create table has failed: '{}' does not exist in column definition".format(col_name)


class TableExistenceError(SqlException):
    message = "Create table has failed: table with same name already exists"


class CharLengthError(SqlException):
    message = "Char length should be over 0"


class NoSuchTable(SqlException):
    message = "No such table"


class DropReferencedTableError(SqlException):
    def __init__(self, table_name: str) -> None:
        super().__init__()
        self.message = "Drop table has failed: '{}' is referenced by other table".format(table_name)


class SelectTableExistenceError(SqlException):
    def __init__(self, table_name: str) -> None:
        super().__init__()
        self.message = "Selection has failed: '{}' does not exist".format(table_name)

