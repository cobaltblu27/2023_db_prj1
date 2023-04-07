from lark import Lark
from lark.exceptions import VisitError

from src.SqlTransformer import SqlTransformer

transformer = SqlTransformer()
with open('grammar.lark') as file:
    sql_parser: Lark = Lark(file.read(), start="command", lexer="basic")


def pytest_reset():
    global transformer
    transformer.TEST_reset_db()


def run(sql: str):
    tree = sql_parser.parse(sql)
    try:
        transformer.transform(tree)
    except VisitError as e:
        raise e.orig_exc


