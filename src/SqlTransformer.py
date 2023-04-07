import os
import sys

from berkeleydb import db
from lark import Transformer

from src.Schema import Schema, ColumnDict, ColumnSpec, KeySpec, ForeignKey
from src.errors import DuplicateColumnDefError, DuplicatePrimaryKeyDefError, ReferenceTypeError
from src.tools import db_keys, print_desc, tree_to_column_list

DB_DIR = "DB"
SCHEMA_DB = 'schema.db'
MAIN_DB = 'db.db'


# 명령어에 따라 어떤 명령어가 요청되었는지 출력하도록 한다.
class SqlTransformer(Transformer):
    def __init__(self):
        super().__init__()
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)

        self._env = db.DBEnv()
        self._env.open(os.path.join(os.getcwd(), DB_DIR),
                       db.DB_CREATE | db.DB_INIT_MPOOL)

        self.schema_db = db.DB(self._env)
        self.schema_db.open(SCHEMA_DB, db.DB_BTREE, db.DB_CREATE)

        self.db = db.DB(self._env)
        self.db.open(MAIN_DB, db.DB_BTREE, db.DB_CREATE)

    def __del__(self):
        self._env.close()
        self.db.close()
        self.schema_db.close()
        pass

    def _print_log(self, query: str):
        print("'{}' requested".format(query))

    def create_table_query(self, items):
        table_name = items[2].children[0].lower()
        column_definition_iter = list(items[3].find_data("column_definition"))
        column_dict: ColumnDict = {}
        for col in column_definition_iter:
            col_name = list(col.find_data("column_name"))[0].children[0].value
            attr_type = list(col.find_data("data_type"))[0].children[0].value
            not_null = str(col.children[2]).upper() == "NOT" and \
                str(col.children[3]).upper() == "NULL"
            length = None if attr_type.lower() != "char" else \
                list(col.find_data("data_type"))[0].children[2].value
            spec: ColumnSpec = {
                "type": attr_type,
                "length": length,
                "non_null": not_null,
            }
            if col_name in column_dict:
                raise DuplicateColumnDefError
            column_dict[col_name] = spec

        key_spec: KeySpec = {
            "primary_key": [],
            "foreign_key": []
        }
        for constraint in items[3].find_data("table_constraint_definition"):
            p_key = list(constraint.find_data("primary_key_constraint"))
            f_key = list(constraint.find_data("referential_constraint"))
            if p_key:
                col_list = tree_to_column_list(p_key[0].children[2])
                if key_spec['primary_key']:
                    raise DuplicatePrimaryKeyDefError
                key_spec['primary_key'] = col_list
            elif f_key:
                col_list = tree_to_column_list(f_key[0].children[2])
                ref_table = f_key[0].children[4].children[0]
                ref_columns = tree_to_column_list(f_key[0].children[5])
                foreign_key_constraint: ForeignKey = {
                    "columns": col_list,
                    "table": ref_table,
                    "ref_columns": ref_columns
                }
                ref_schema = Schema.schema_from_key(self.schema_db, ref_table)

                if len(col_list) != len(ref_columns):
                    raise ReferenceTypeError
                for i in range(len(col_list)):
                    col_spec = column_dict[col_list[i]]
                    ref_col_spec = ref_schema.columns[ref_columns[i]]
                    if col_spec != ref_col_spec:
                        raise ReferenceTypeError

                key_spec['foreign_key'].append(foreign_key_constraint)

        schema = Schema(table_name, column_dict, key_spec)
        schema.commit_schema(self.schema_db)

    def select_query(self, items):
        self._print_log("SELECT")

    def insert_query(self, items):
        self._print_log("INSERT")

    def drop_query(self, items):
        self._print_log("DROP TABLE")

    def _describe_db(self, name: str):
        Schema.schema_from_key(self.schema_db, name).describe()

    def explain_query(self, items):
        table = items[1].children[0].value
        self._describe_db(table)

    def describe_query(self, items):
        table = items[1].children[0].value
        self._describe_db(table)

    def desc_query(self, items):
        table = items[1].children[0].value
        self._describe_db(table)

    def show_query(self, items):
        keys = filter(
            lambda k: "columns" in k,
            db_keys(self.schema_db)
        )
        print_desc([[key.split("$$")[0]] for key in keys])

    def delete_query(self, items):
        self._print_log("DELETE")

    def update_query(self, items):
        self._print_log("UPDATE")

    def EXIT(self, items):
        sys.exit()
