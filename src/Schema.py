import json
from typing import Dict, Literal, TypedDict, List
import berkeleydb

from src.tools import s2b

AttributeType = Literal["int", "char", "date"]
Constraints = Literal["non-null", "p_key", "f_key"]


class ColumnSpec(TypedDict):
    type: AttributeType
    constraints: List[Constraints]


ColumnDict = Dict[str, ColumnSpec]


class Schema:
    def __init__(self, name: str, columns: ColumnDict):
        self.name: str = name
        self.columns = columns

    def get_key(self, attr: str) -> bytes:
        return s2b("{}$${}".format(self.name, attr))

    def commit_schema(self, schema_db: berkeleydb.db.DB):
        schema_db.put(s2b(self.name), s2b(json.dumps(self.columns)))

    @staticmethod
    def schema_from_key(db: berkeleydb.db.DB, name: str) -> 'Schema':
        attrs = db.get(s2b(name))
        return Schema(name, attrs)
