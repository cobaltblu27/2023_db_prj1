import sys
from typing import List, Union, cast

from lark import Transformer

from src.DataBase import SchemaDB, RowsDB
from src.Schema import Schema
from src.Types import ForeignKey, ColumnSpec, ColumnDict, KeySpec
from src.errors import *
from src.tools import PROMPT, print_desc, tree_to_column_list, print_table, search_item


# 명령어에 따라 어떤 명령어가 요청되었는지 출력하도록 한다.
class SqlTransformer(Transformer):
    # row_db에는 row의 실제 값들이, schema_db에는 메타데이터, row reference list 등 다른 모든 정보가 저장된다.
    def __init__(self):
        super().__init__()
        self.schema_db = SchemaDB()
        self.row_db = RowsDB()

    def TEST_reset_db(self):
        self.row_db.reset()
        self.schema_db.reset()

    def _print_log(self, query: str):
        print("'{}' requested".format(query))

    def _schema_from_key(self, name: str):
        return Schema.schema_from_key(self.schema_db, name)

    # column/key specification은 Schema 클래스로 만들어진다.
    # 생성된 schema 인스턴스는 commit 메서드 호출 시 self.schema_db
    # 에 저장된다.
    def create_table_query(self, items):
        table_name = items[2].children[0].lower()
        if table_name in self.schema_db.get_table_names():
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
                        raise NonExistingColumnDefError(p_key_col)
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
                if ref_table not in self.schema_db.get_table_names():
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
                        raise NonExistingColumnDefError(col_list[i])
                    col_spec = column_dict[col_list[i]]
                    ref_col_spec = ref_schema.columns[ref_columns[i]]
                    if col_spec['type'] != ref_col_spec['type'] or \
                            col_spec['length'] != ref_col_spec['length']:
                        raise ReferenceTypeError

                key_spec['foreign_key'].append(foreign_key_constraint)

        schema = Schema(table_name, column_dict, key_spec)
        schema.commit_schema(self.schema_db)

    def select_query(self, items):
        table_name = search_item(items, "table_name")
        if table_name not in self.schema_db.get_table_names():
            raise SelectTableExistenceError(table_name)
        target_schema = Schema.schema_from_key(self.schema_db, table_name)

        column_names = []
        for subtree in items[1].iter_subtrees():
            if subtree.data == "column_name":
                column_names.append(subtree.children[0].value)
        if len(column_names) < 1:
            column_names = list(target_schema.columns.keys())

        refs = self.schema_db.get_refs(target_schema.name)
        result = [target_schema.select(self.row_db, ref) for ref in refs]

        result_table = [cast(List[Union[int, str]], column_names)]
        for row in result:
            result_table.append(["null" if column not in row else row[column] for column in column_names])
        print_table(result_table)

    # Row 정보는 self.row_db에 저장된다. key값은 primary key들의 json이며, 전체 row의
    # primary key값들의 목록은 self.schema_db에 저장된다.
    def insert_query(self, items):
        print(items)
        columns_specs_token = items[3]
        # table_name = list(items[2].find_data("table_name"))[0].children[0]
        table_name = search_item(items, "table_name")
        if table_name not in self.schema_db.get_table_names():
            raise NoSuchTable
        target_schema = self._schema_from_key(table_name)
        column_specs: List[str] = list(target_schema.columns.keys())
        if columns_specs_token is not None:
            column_specs = [
                col.children[0].value for col in items[3].find_data("column_name")]
            for column_spec in column_specs:
                if column_spec not in target_schema.columns.keys():
                    raise InsertColumnExistenceError(column_spec)

        input_values_list = items[5].find_data("comparable_value")
        column_token = [col.children[0] for col in input_values_list]  # {type, value}[]
        column_dict = {}

        # validation
        if len(column_specs) != len(column_token):
            raise InsertTypeMismatchError
        for i, column in enumerate(column_specs):
            if not target_schema.validate_type(column, column_token[i].type):
                raise InsertTypeMismatchError
            column_dict[column] = column_token[i].value
        for name, spec in target_schema.columns.items():
            if spec["non_null"] and name not in column_dict:
                raise InsertColumnNonNullableError(name)

        # TODO: add validation. As of prj1-2, no validation is needed
        target_schema.insert(self.schema_db, self.row_db, column_dict)

        print("{} The row is inserted".format(PROMPT))

    def drop_query(self, items):
        table_to_drop = items[2].children[0].lower()
        table_names = self.schema_db.get_table_names()

        if table_to_drop not in table_names:
            raise NoSuchTable
        for table_name in table_names:
            if table_name == table_to_drop:
                continue
            table_schema = self._schema_from_key(table_name)
            for f_key in table_schema.key_spec['foreign_key']:
                if f_key["table"] == table_to_drop:
                    raise DropReferencedTableError(table_to_drop)

        target_schema = self._schema_from_key(table_to_drop)
        row_refs = self.schema_db.get_refs(target_schema.name)
        for row in row_refs:
            target_schema.delete(self.schema_db, self.row_db, row)

        self.schema_db.drop(table_to_drop)
        print("{} '{}' table is dropped".format(PROMPT, table_name))

    def _describe_db(self, name: str):
        table_names = self.schema_db.get_table_names()
        if name not in table_names:
            raise NoSuchTable
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
        names = self.schema_db.get_table_names()
        print_desc([[table] for table in names])

    def delete_query(self, items):

        pass

    def update_query(self, items):
        self._print_log("UPDATE")

    def EXIT(self, items):
        sys.exit()
