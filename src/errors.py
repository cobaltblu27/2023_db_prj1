class SyntaxError(Exception):
    pass


class CreateTableSuccess(Exception):
    pass


class DuplicateColumnDefError(Exception):
    pass


class DuplicatePrimaryKeyDefError(Exception):
    pass


class ReferenceTypeError(Exception):
    pass


class ReferenceNonPrimaryKeyError(Exception):
    pass


class ReferenceColumnExistenceError(Exception):
    pass


class ReferenceTableExistenceError(Exception):
    pass


class NonExistingColumnDefError(Exception):
    pass


class TableExistenceError(Exception):
    pass


class CharLengthError(Exception):
    pass


class DropSuccess(Exception):
    pass


class NoSuchTable(Exception):
    pass


class DropReferencedTableError(Exception):
    pass


class InsertResult(Exception):
    pass


class SelectTableExistenceError(Exception):
    pass
