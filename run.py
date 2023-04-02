import sys
import argparse
from typing import Generator
from lark import Lark, Transformer, ParseTree, exceptions

PROMPT = "DB_2016-19965>"

# (테스트용) argument로 query를 받을 수 있게 하였다.
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-t", "--test", type=str, help="test string")


# 명령어에 따라 어떤 명령어가 요청되었는지 출력하도록 한다.
class SqlTransformer(Transformer):
    def _print_log(self, query: str):
        print("{} '{}' requested".format(PROMPT, query))

    def create_table_query(self, items):
        self._print_log("CREATE TABLE")
    
    def select_query(self, items):
        self._print_log("SELECT")

    def insert_query(self, items):
        self._print_log("INSERT")

    def drop_query(self, items):
        self._print_log("DROP TABLE")

    def explain_query(self, items):
        self._print_log("EXPLAIN")

    def describe_query(self, items):
        self._print_log("DESCRIBE")

    def desc_query(self, items):
        self._print_log("DESC")

    def show_query(self, items):
        self._print_log("SHOW")

    def delete_query(self, items):
        self._print_log("DELETE")

    def update_query(self, items):
        self._print_log("UPDATE")

    def EXIT(self, items):
        sys.exit()


# semicolon 기준으로 쿼리를 분리하여 parser에 넣을 str을 생성해 주는 generator
def get_prompt_input() -> Generator[str, None, None]:
    while True:
        str_input: str = input(PROMPT + " ")
        while str_input[-1] != ';':
            next_line: str = input()
            str_input += " " + next_line
            str_input = str_input.strip()

        while str_input.find(';') != len(str_input) - 1:
            split_idx = str_input.find(';')
            yield str_input[:split_idx + 1]
            str_input = str_input[split_idx + 1:].strip()
        yield str_input


# 루프를 돌며 한번에 한 명령어를 parsing한다.
def prompt(parser: Lark, transformer: Transformer):
    input_generator = get_prompt_input()
    while True:
        try:
            query_str = next(input_generator)
            tree: ParseTree = parser.parse(query_str)
            transformer.transform(tree)
        except exceptions.UnexpectedToken:
            print("{} Syntax Error".format(PROMPT))
            input_generator = get_prompt_input()  # 에러가 날 경우 저장된 다음 명령어들을 버린다.


if __name__ == "__main__":
    with open('grammar.lark') as file:
        sql_parser = Lark(file.read(), start="command", lexer="basic")

    transformer = SqlTransformer()

    args = arg_parser.parse_args()
    test_str = args.test

    if test_str is not None:
        output: ParseTree = sql_parser.parse(test_str)
        print("----------Parsed result----------")
        print(output.pretty())
        print("----------Tree----------")
        print(output)
    else:
        prompt(sql_parser, transformer)
