import argparse
import sys
from typing import Generator

from lark import Lark, Transformer, ParseTree, exceptions

from src.Schema import Schema
from src.SqlTransformer import SqlTransformer
from src.errors import *
from src.tools import PROMPT

# (테스트용) argument로 query를 받을 수 있게 하였다.
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-t", "--test", type=str, help="test string")


# arg_parser.add_argument("-d", "--debug", type=bool, help="show tree and parsed result")


# semicolon 기준으로 쿼리를 분리하여 parser에 넣을 str을 생성해 주는 generator
def get_prompt_input() -> Generator[str, None, None]:
    while True:
        str_input: str = input(PROMPT + " ")
        if len(str_input) == 0:
            continue
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
            try:
                transformer.transform(tree)
            except exceptions.VisitError as e:
                raise e.orig_exc
        except exceptions.UnexpectedToken:
            print("{} Syntax Error".format(PROMPT))
            input_generator = get_prompt_input()  # 에러가 날 경우 저장된 다음 명령어들을 버린다.
        except KeyboardInterrupt:
            sys.exit(-1)
        except SqlException as e:
            # SqlException에 해당하는 에러 발생 시 메세지 출력 후 다시 루프를 돈다.
            print("{} {}".format(PROMPT, e.message))


if __name__ == "__main__":
    with open('grammar.lark') as file:
        sql_parser = Lark(file.read(), start="command", lexer="basic")

    transformer = SqlTransformer()

    args = arg_parser.parse_args()
    test_str = args.test

    if test_str is not None:
        print("requested:")
        print(test_str)
        tree: ParseTree = sql_parser.parse(test_str)
        # print("----------Parsed result----------")
        # print(tree.pretty())
        # print("----------Tree----------")
        # print(tree)
        transformer.transform(tree)
    else:
        prompt(sql_parser, transformer)
