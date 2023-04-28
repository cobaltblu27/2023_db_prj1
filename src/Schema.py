import itertools
from typing import List

from src.DataBase import SchemaDB, RowsDB
from src.Types import ColumnDict, KeySpec, ColumnValue
from src.tools import print_desc


# Schema 클래스는 한 table을 나타내는 역할을 한다. 각 테이블 관련해서 DataBase와
# 상호작용하는 부분은 이 layer을 거치도록 하였다. SqlTransformer에선 이
# 클래스의 메서드를 호출함으로서 파싱된 쿼리를 실제로 실행한다.
# Schema는 create table에서 직접 새 __init__을 거쳐 새 Schema를 만드는 방법,
# 그리고 아래의 static method 를 활용하여 기존의 table로부터 만드는 방법이 있다.
class Schema:
    def __init__(self, name: str, columns: ColumnDict, key_spec: KeySpec):
        self.name: str = name
        self.columns = columns
        self.key_spec = key_spec

    def get_pkey_col_list(self) -> List[str]:
        return self.key_spec["primary_key"]

    def commit_schema(self, schema_db: SchemaDB):
        schema_db.put_column(self.name, self.columns)
        schema_db.put_key_spec(self.name, self.key_spec)

    def insert(self, schema_db: SchemaDB, db: RowsDB, column: ColumnValue):
        p_key_list = self.get_pkey_col_list()
        row_refs = schema_db.get_refs(self.name)
        ref_dict = {k: v for k, v in column.items() if k in p_key_list}
        db.put_row(self.name, ref_dict, column)
        schema_db.put_refs(self.name, row_refs + [ref_dict])

    def select(self, db: RowsDB, ref: object) -> ColumnValue:
        return db.get_row(self.name, ref)

    def delete(self, schema_db: SchemaDB, db: RowsDB, delete_ref):
        row_refs = schema_db.get_refs(self.name)
        row_refs = list(filter(lambda ref: ref != delete_ref, row_refs))
        db.delete_row(self.name, delete_ref)
        schema_db.put_refs(self.name, row_refs)

    def describe(self):
        table = [
            ["table_name", self.name, '', ''],
            ["column_name", "type", "null", "key"]
        ]
        ref_cols_list = [f_keys['columns']
                         for f_keys in self.key_spec['foreign_key']]
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
    def schema_from_key(db: SchemaDB, name: str) -> 'Schema':
        col = db.get_columns(name)
        keys = db.get_key_spec(name)
        return Schema(name, col, keys)
