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
        self.message = "Create table has failed: '[{}]' does not exist in column definition".format(col_name)


class TableExistenceError(SqlException):
    message = "Create table has failed: table with same name already exists"


class CharLengthError(SqlException):
    message = "Char length should be over 0"


class NoSuchTableError(SqlException):
    message = "No such table"


class DropReferencedTableError(SqlException):
    def __init__(self, table_name: str) -> None:
        super().__init__()
        self.message = "Drop table has failed: '{}' is referenced by other table".format(table_name)


class SelectTableExistenceError(SqlException):
    def __init__(self, table_name: str) -> None:
        super().__init__()
        self.message = "Selection has failed: '{}' does not exist".format(table_name)


class InsertResult(SqlException):
    message = "The row is inserted"


class InsertTypeMismatchError(SqlException):
    message = "Insertion has failed: Types are not matched"


class InsertColumnExistenceError(SqlException):
    def __init__(self, col_name: str):
        super().__init__()
        self.message = "Insertion has failed: '{}' does not exist".format(col_name)


class InsertColumnNonNullableError(SqlException):
    def __init__(self, col_name: str):
        super().__init__()
        self.message = "Insertion has failed: '{}' is not nullable".format(col_name)


class DeleteResult(SqlException):
    def __init__(self, count: int):
        super().__init__()
        self.message = "‘{}’ row(s) are deleted".format(count)


class SelectColumnResolveError(SqlException):
    def __init__(self, col_name: str):
        super().__init__()
        self.message = "Selection has failed: fail to resolve '{}'".format(col_name)


class WhereIncomparableError(SqlException):
    message = "Where clause trying to compare incomparable values"


class WhereTableNotSpecified(SqlException):
    message = "Where clause trying to reference tables which are not specified"


class WhereColumnNotExist(SqlException):
    message = "Where clause trying to reference non existing column"


class WhereAmbiguousReference(SqlException):
    message = "Where clause contains ambiguous reference"


class InsertDuplicatePrimaryKeyError(SqlException):
    message = "Insertion has failed: Primary key duplication"


class InsertReferentialIntegrityError(SqlException):
    message = "Insertion has failed: Referential integrity violation"


class DeleteReferentialIntegrityPassed(SqlException):
    def __init__(self, count: int):
        super().__init__()
        self.message = "‘{}’ row(s) are not deleted due to referential integrity".format(count)

