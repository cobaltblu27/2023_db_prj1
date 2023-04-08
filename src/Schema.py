import itertools
import json
from typing import Dict, Literal, Optional, Tuple, TypedDict, List, Union

import berkeleydb

from src.tools import s2b, print_desc, ENCODING

AttributeType = Literal["int", "char", "date"]
Constraints = Literal["non-null", "p_key", "f_key"]


class ColumnSpec(TypedDict):
    type: AttributeType
    length: Union[None, int]
    non_null: bool


class ForeignKey(TypedDict):
    columns: List[str]
    table: str
    ref_columns: List[str]


class KeySpec(TypedDict):
    primary_key: List[str]
    foreign_key: List[ForeignKey]


ColumnDict = Dict[str, ColumnSpec]


class Schema:
    def __init__(self, name: str, columns: ColumnDict, key_spec: KeySpec):
        self.name: str = name
        self.columns = columns
        self.key_spec = key_spec

    def get_key(self, attr: str) -> bytes:
        return s2b(self.name, attr)
    
    def get_pkey_col_list(self) -> List[str]:
        return self.key_spec["primary_key"]

    # store list of each row's pkeys into db for keeping reference to each rows
    def get_row_refs(self, db: berkeleydb.db.DB):
        ref_list = db.get(s2b(self.name, "pkeys"))
        if ref_list is None:
            return []
        return json.loads(ref_list.decode(ENCODING))

    def commit_schema(self, schema_db: berkeleydb.db.DB):
        column_key = s2b(self.name, "columns")
        key_spec_key = s2b(self.name, "key_spec")
        schema_db.put(column_key, s2b(json.dumps(self.columns)))
        schema_db.put(key_spec_key, s2b(json.dumps(self.key_spec)))

    def insert(self, db: berkeleydb.db.DB, column: Dict[str, Union[int, str]]):
        p_key_list = self.get_pkey_col_list()
        row_refs = self.get_row_refs(db)
        p_key_values = [column[k] for k in p_key_list]
        db.put(s2b(self.name, *p_key_values), s2b(json.dumps(column)))
        db.put(s2b(self.name, "pkeys"), s2b(json.dumps([p_key_values] + row_refs)))

    def select(self, db: berkeleydb.db.DB, p_key_values) -> Dict[str, Union[int, str]]:
        value_raw = db.get(s2b(self.name, *p_key_values))
        value_dict = json.loads(value_raw.decode(ENCODING))
        return value_dict

    def delete(self, db: berkeleydb.db.DB, p_key_values):
        row_refs = self.get_row_refs(db)
        row_refs = list(filter(lambda ref: ref != p_key_values, row_refs))
        db.delete(s2b(self.name, *p_key_values))
        db.put(s2b(self.name, "pkeys"), s2b(json.dumps(row_refs)))

    def describe(self):
        table = [
            ["table_name", self.name, '', ''],
            ["column_name", "type", "null", "key"]
        ]
        ref_cols_list = [f_keys['columns'] for f_keys in self.key_spec['foreign_key']]
        ref_cols = list(itertools.chain.from_iterable(ref_cols_list))
        for col_name in self.columns:
            col_type: str = self.columns[col_name]['type']
            if col_type == "char":
                col_type = "char({})".format(self.columns[col_name]['length'])
            non_null = "N" if self.columns[col_name]['non_null'] else "Y"
            key_constraint = ""
            if col_name in ref_cols:
                key_constraint = "FOR"
            if col_name in self.key_spec['primary_key']:
                key_constraint = "PRI"
            desc_row = [col_name, col_type, non_null, key_constraint]
            table.append(desc_row)
        print_desc(table)
        pass

    @staticmethod
    def schema_from_key(db: berkeleydb.db.DB, name: str) -> 'Schema':
        col_raw = db.get(s2b(name, "columns")).decode(ENCODING)
        col = json.loads(col_raw)
        keys_raw = db.get(s2b(name, "key_spec")).decode(ENCODING)
        keys = json.loads(keys_raw)
        return Schema(name, col, keys)
