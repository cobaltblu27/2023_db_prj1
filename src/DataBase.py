import json
import os
from typing import Dict, List, Union

from berkeleydb import db

from src.Types import ColumnDict, KeySpec
from src.tools import ENCODING, db_keys, s2b

DB_DIR = "DB"
SCHEMA_DB = 'schema.db'
MAIN_DB = 'db.db'

_env: db.DBEnv = None
_db_cnt = 0


class DataBase:
    def __init__(self):
        super().__init__()
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)
        global _env, _db_cnt
        _db_cnt += 1
        if _env is None:
            _env = db.DBEnv()
            _env.open(os.path.join(os.getcwd(), DB_DIR),
                      db.DB_CREATE | db.DB_INIT_MPOOL)

        self._env = _env
        self.db = db.DB(self._env)
        self.db.open(SCHEMA_DB, db.DB_BTREE, db.DB_CREATE)

    def reset(self):
        cursor = self.db.cursor()
        record = cursor.first()
        while record:
            key, _ = record
            self.db.delete(key)
            record = cursor.next()

    def __del__(self):
        global _db_cnt, _env
        _db_cnt -= 1
        if _db_cnt == 0:
            _env.close()
        self.db.close()


class SchemaDB(DataBase):
    def __init__(self):
        super().__init__()

    def put_column(self, schema_name: str, columns: ColumnDict):
        column_key = s2b(schema_name, "columns")
        self.db.put(column_key, s2b(json.dumps(columns)))

    def put_key_spec(self, schema_name: str, keys: KeySpec):
        key_key = s2b(schema_name, "keys_spec")
        self.db.put(key_key, s2b(json.dumps(keys)))

    def put_refs(self, schema_name: str, row_refs: List[object]):
        pkey_key = s2b(schema_name, "pkeys")
        self.db.put(pkey_key, s2b(json.dumps(row_refs)))

    def get_columns(self, name: str) -> ColumnDict:
        col_raw = self.db.get(s2b(name, "columns"))
        if col_raw is None:
            return {}
        return json.loads(col_raw.decode(ENCODING))

    def get_key_spec(self, name: str) -> KeySpec:
        keys_raw = self.db.get(s2b(name, "keys_spec"))
        if keys_raw is None:
            raise Exception
        return json.loads(keys_raw.decode(ENCODING))

    def get_refs(self, name: str) -> List[object]:
        pkeys_raw = self.db.get(s2b(name, "pkeys"))
        if pkeys_raw is None:
            return []
        return json.loads(pkeys_raw.decode(ENCODING))

    def get_table_names(self) -> List[str]:
        keys = filter(
            lambda k: "columns" in k,
            db_keys(self.db)
        )
        names = [key.split("$$")[0] for key in keys]
        return list(set(names))

    def drop(self, name: str):
        keys_to_delete = filter(
            lambda k: name in k,
            db_keys(self.db)
        )
        for k in keys_to_delete:
            self.db.delete(s2b(k))


class RowsDB(DataBase):
    def __init__(self):
        super().__init__()

    def put_row(self, table_name: str, key: object, value: object):
        key = s2b(table_name, json.dumps(key))
        self.db.put(key, s2b(json.dumps(value)))

    def get_row(self, table_name: str, key: object) -> Dict[str, Union[int, str]]:
        key = s2b(table_name, json.dumps(key))
        return json.loads(self.db.get(key).decode(ENCODING))

    def delete_row(self, table_name: str, key: object):
        key = s2b(table_name, json.dumps(key))
        self.db.delete(key)
