import json
import os
import sys
from typing import List

from berkeleydb import db
from lark import Transformer, Token

from src.Schema import Schema, ColumnDict, ColumnSpec
from src.tools import s2b, db_keys, print_table, ENCODING, print_desc

DB_DIR = "../DB"
SCHEMA_DB = 'schema.db'
MAIN_DB = 'db.db'


# 명령어에 따라 어떤 명령어가 요청되었는지 출력하도록 한다.
class SqlTransformer(Transformer):
    def __init__(self):
        super().__init__()
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)

        self._env = db.DBEnv()
        self._env.open(os.path.join(os.getcwd(), DB_DIR), db.DB_CREATE | db.DB_INIT_MPOOL)

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
            spec: ColumnSpec = {
                "type": attr_type,
                "constraints": []
            }
            if not_null:
                spec["constraints"].append("non-null")
            column_dict[col_name] = spec
        schema = Schema(table_name, column_dict)
        schema.commit_schema(self.schema_db)
        self._print_log("CREATE TABLE")

    def select_query(self, items):
        self._print_log("SELECT")

    def insert_query(self, items):
        self._print_log("INSERT")

    def drop_query(self, items):
        self._print_log("DROP TABLE")

    def _describe_db(self, name: str):
        col_raw: bytes = self.schema_db.get(s2b(name))
        cols: ColumnDict = json.loads(col_raw.decode(ENCODING))
        table = [
            ["table_name", name, '', ''],
            ["column_name", "type", "null", "key"]
        ]
        for key in list(cols):
            desc_row = [
                key,
                cols[key]["type"],
                "not null" if "non-null" in cols[key]["constraints"] else "",
                ""]
            table.append(desc_row)
        print_desc(table)

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
        keys = db_keys(self.schema_db)
        print_desc([[key] for key in keys])

    def delete_query(self, items):
        self._print_log("DELETE")

    def update_query(self, items):
        self._print_log("UPDATE")

    def EXIT(self, items):
        sys.exit()
