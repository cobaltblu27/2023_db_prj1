from typing import List

import berkeleydb
from lark import Tree

ENCODING = "utf-8"


def s2b(*strings) -> bytes:
    key = "$$".join(strings)
    return key.encode(ENCODING)


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


def _print_separator(column_widths: List[int]):
    for width in column_widths:
        print('+' + '-' * (width + 2), end='')
    print('+')


def db_clear(db: berkeleydb.db.DB):
    cursor = db.cursor()
    record = cursor.first()
    while record:
        key, value = record
        db.delete(key)
        record = cursor.next()


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


def print_table(table: List[List[str]]):
    height = len(table[0])
    column_widths = [max(len(str(row[i])) for row in table) for i in range(height)]
    _print_separator(column_widths)
    for i, row in enumerate(table):
        for j, cell in enumerate(row):
            print('|', f"{cell: <{column_widths[j]}}", end=' ')
        print('|')
        if i == 0:
            _print_separator(column_widths)
    _print_separator(column_widths)


def print_desc(table: List[List[str]]):
    height = len(table[0])
    column_widths = [max(len(str(row[i])) for row in table) for i in range(height)]
    total_width = sum(column_widths) + len(column_widths)
    print("-" * total_width)
    for row in table:
        for i, cell in enumerate(row):
            print(f"{cell: <{column_widths[i]}}", end=' ')
        print('')
    print("-" * total_width)


if __name__ == "__main__":
    data = [
        ["ACCOUNT_NUMBER", "BRANCH_NAME", "BALANCE"],
        ["A-101", "Downtown", "500"],
        ["A-102", "Perryridge", "400"],
        ["A-201", "Brighton", "900"],
    ]
    print_table(data)
