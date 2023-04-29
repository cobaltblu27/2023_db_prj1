import json
from typing import List, Union

# cyclic dependency를 방지하기 위해 전체적으로 사용되는 변수, helper function은 여기 선언한다.
import lark

ENCODING = "utf-8"
PROMPT = "DB_2016-19965>"


def row_key(obj) -> bytes:
    json_str = json.dumps(obj)
    return s2b(json_str)


def schema_key(*strings) -> bytes:
    return s2b(*strings)


# string 여러개를 받아 key값용 bytes로 변환; string2bytes
def s2b(*strings) -> bytes:
    key = "$$".join(strings)
    return key.encode(ENCODING)


def search_item(items, data_name: str):
    for item in items:
        if isinstance(item, lark.Tree):
            res = list(item.find_data(data_name))
            if len(res) > 0:
                children = res[0].children
                return children[0] if len(children) > 0 else None
    return None


def search_items_list(items, data_name: str):
    pass


def db_keys(db):
    key_list = []
    cursor = db.cursor()
    record = cursor.first()
    while record:
        key, _ = record
        key_list.append(key.decode(ENCODING))
        record = cursor.next()
    cursor.close()
    return key_list


# tree_to_column_list input example:
# Tree(
#   Token('RULE', 'column_name_list'),
#   [
#     Token('LP', '('),
#     Tree(
#       Token('RULE', 'column_name'),
#       [Token('IDENTIFIER', 'id')]
#     ),
#     Tree(
#       Token('RULE', 'column_name'),
#       [Token('IDENTIFIER', 'name')]
#     ),
#     Token('RP', ')')
#   ]
# )
def tree_to_column_list(tree) -> List[str]:
    return [col.children[0].value for col in tree.find_data("column_name")]


def _print_separator(column_widths: List[int]):
    for width in column_widths:
        print('+' + '-' * (width + 2), end='')
    print('+')


def print_table(table: List[List[Union[str, int]]]):
    height = len(table[0])
    column_widths = [max(len(str(row[i])) for row in table)
                     for i in range(height)]
    _print_separator(column_widths)
    for i, row in enumerate(table):
        for j, cell in enumerate(row):
            print('|', f"{cell: <{column_widths[j]}}", end=' ')
        print('|')
        if i == 0:
            _print_separator(column_widths)
    _print_separator(column_widths)


def print_desc(table: List[List[str]]):
    if len(table) == 0:
        print("---\n---")
        return
    height = len(table[0])
    column_widths = [max(len(str(row[i])) for row in table)
                     for i in range(height)]
    total_width = sum(column_widths) + len(column_widths)
    print("-" * total_width)
    for row in table:
        for i, cell in enumerate(row):
            print(f"{cell: <{column_widths[i]}}", end=' ')
        print('')
    print("-" * total_width)
