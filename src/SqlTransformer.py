import os
import sys
from typing import List, Union, cast

from berkeleydb import db
from lark import Transformer

from src.Schema import Schema, ColumnDict, ColumnSpec, KeySpec, ForeignKey
from src.errors import *
from src.tools import db_keys, print_desc, s2b, tree_to_column_list, db_clear, print_table

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

    def TEST_reset_db(self):
        db_clear(self.db)
        db_clear(self.schema_db)

    def _print_log(self, query: str):
        print("'{}' requested".format(query))

    def _get_table_names(self) -> List[str]:
        keys = filter(
            lambda k: "columns" in k,
            db_keys(self.schema_db)
        )
        return [key.split("$$")[0] for key in keys]

    def _schema_from_key(self, name: str):
        return Schema.schema_from_key(self.schema_db, name)

    def create_table_query(self, items):
        table_name = items[2].children[0].lower()
        if table_name in self._get_table_names():
            raise TableExistenceError
        column_definition_iter = list(items[3].find_data("column_definition"))
        column_dict: ColumnDict = {}
        for col in column_definition_iter:
            col_name = list(col.find_data("column_name"))[0].children[0].value
            attr_type = list(col.find_data("data_type"))[0].children[0].value
            not_null = str(col.children[2]).upper() == "NOT" and \
                       str(col.children[3]).upper() == "NULL"
            length = None if attr_type.lower() != "char" else \
                int(list(col.find_data("data_type"))[0].children[2].value)
            if length is not None and length < 1:
                raise CharLengthError
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
                for p_key_col in col_list:
                    if p_key_col not in column_dict:
                        raise NonExistingColumnDefError
                    column_dict[p_key_col]['non_null'] = True
            elif f_key:
                col_list = tree_to_column_list(f_key[0].children[2])
                ref_table = f_key[0].children[4].children[0]
                ref_columns = tree_to_column_list(f_key[0].children[5])
                foreign_key_constraint: ForeignKey = {
                    "columns": col_list,
                    "table": ref_table,
                    "ref_columns": ref_columns
                }
                if ref_table not in self._get_table_names():
                    raise ReferenceTableExistenceError
                ref_schema = self._schema_from_key(ref_table)

                if any([ref_col not in ref_schema.columns for ref_col in ref_columns]):
                    raise ReferenceColumnExistenceError
                if ref_columns != ref_schema.get_pkey_col_list():
                    raise ReferenceNonPrimaryKeyError
                if len(col_list) != len(ref_columns):
                    raise ReferenceTypeError
                for i in range(len(col_list)):
                    if col_list[i] not in column_dict:
                        raise NonExistingColumnDefError
                    col_spec = column_dict[col_list[i]]
                    ref_col_spec = ref_schema.columns[ref_columns[i]]
                    if col_spec['type'] != ref_col_spec['type'] or \
                            col_spec['length'] != ref_col_spec['length']:
                        raise ReferenceTypeError

                key_spec['foreign_key'].append(foreign_key_constraint)

        schema = Schema(table_name, column_dict, key_spec)
        schema.commit_schema(self.schema_db)

    def select_query(self, items):
        table_name = list(items[2].find_data("table_name"))[0].children[0]
        if table_name not in self._get_table_names():
            raise SelectTableExistenceError

        target_schema = Schema.schema_from_key(self.schema_db, table_name)
        refs = target_schema.get_row_refs(self.db)
        result = [target_schema.select(self.db, ref) for ref in refs]

        columns_names = list(target_schema.columns.keys())
        result_table = [cast(List[Union[int, str]], columns_names)]
        for row in result:
            result_table.append([row[column] for column in columns_names])
        print_table(result_table)

    def insert_query(self, items):
        columns_specs_token = items[3]
        table_name = list(items[2].find_data("table_name"))[0].children[0]
        if table_name not in self._get_table_names():
            raise NoSuchTable
        target_schema = self._schema_from_key(table_name)
        column_specs: List[str] = list(target_schema.columns.keys())
        if columns_specs_token is not None:
            column_specs = [col.children[0].value for col in items[3].find_data("column_name")]
        column_values = [col.children[0].value for col in items[5].find_data("comparable_value")]
        column_dict = {}
        for i, column in enumerate(column_specs):
            column_dict[column] = column_values[i]

        # TODO: add validation. As of prj1-2, no validation is needed
        target_schema.insert(self.db, column_dict)

    def drop_query(self, items):
        table_to_drop = items[2].children[0].lower()
        table_names = self._get_table_names()

        if table_to_drop not in table_names:
            raise NoSuchTable
        for table_name in table_names:
            if table_name == table_to_drop:
                continue
            table_schema = self._schema_from_key(table_name)
            for f_key in table_schema.key_spec['foreign_key']:
                if f_key["table"] == table_to_drop:
                    raise DropReferencedTableError

        target_schema = self._schema_from_key(table_to_drop)
        row_refs = target_schema.get_row_refs(self.db)
        for row in row_refs:
            target_schema.delete(self.db, row)

        keys_to_delete = filter(
            lambda k: table_to_drop in k,
            db_keys(self.schema_db)
        )
        for k in keys_to_delete:
            self.schema_db.delete(s2b(k))

        self._print_log("DROP TABLE")

    def _describe_db(self, name: str):
        self._schema_from_key(name).describe()

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
        print_desc([[table] for table in self._get_table_names()])

    def delete_query(self, items):
        self._print_log("DELETE")

    def update_query(self, items):
        self._print_log("UPDATE")

    def EXIT(self, items):
        sys.exit()
