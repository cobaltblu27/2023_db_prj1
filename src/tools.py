from typing import List

ENCODING = "utf-8"


def s2b(string: str) -> bytes:
    return string.encode(ENCODING)


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


def print_table(table: List[List[str]]):
    height = len(table[0])
    column_widths = [max(len(str(row[i])) for row in table) for i in range(height)]
    _print_separator(column_widths)
    for row in table:
        for i, cell in enumerate(row):
            print('|', f"{cell: <{column_widths[i]}}", end=' ')
        print('|')
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
