import sys
import argparse
from typing import Generator
from lark import Lark, Transformer, ParseTree, exceptions, Token

PROMPT = "DB_2016-19965> "
query_node_map = {
    'create_table_query': 'CREATE TABLE',
    'select_query': 'SELECT',
    'insert_query': 'INSERT',
    'drop_query': 'DROP TABLE',
    'explain_query': 'EXPLAIN',
    'describe_query': 'DESCRIBE',
    'show_query': 'SHOW',
    'delete_query': 'DELETE',
    'update_query': 'UPDATE',
}
EXIT = 'EXIT'

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-t", "--test", type=str, help="test string")


class MyTransformer(Transformer):
    def create_table_query(self, items):
        pass
        # implemet here

    def drop_table_query(self, items):
        pass
        # implemet here

    def exit(self):
        sys.exit()


def check_exit(tree: ParseTree) -> bool:
    matching_nodes = tree.scan_values(lambda n: isinstance(n, Token) and n.type == EXIT)
    return len(list(matching_nodes)) > 0


def get_query_description(tree: ParseTree) -> str:
    nodes = tree.find_pred(lambda node: node.data in query_node_map.keys())
    query_node = list(nodes)[0]
    return query_node.children[0].type


def get_prompt_input() -> Generator[str, None, None]:
    while True:
        str_input: str = input(PROMPT)
        while str_input[-1] != ';':
            next_line: str = input()
            str_input += " " + next_line
            str_input = str_input.strip()

        while str_input.find(';') != len(str_input) - 1:
            split_idx = str_input.find(';')
            yield str_input[:split_idx + 1]
            str_input = str_input[split_idx + 1:].strip()
        yield str_input


def prompt(parser: Lark, transformer: Transformer):
    input_generator = get_prompt_input()
    loop = True
    while loop:
        try:
            query_str = next(input_generator)
            tree: ParseTree = parser.parse(query_str)
            if check_exit(tree):
                break
            query_name = get_query_description(tree)
            print("{}{} requested".format(PROMPT, query_name))
            transformer.transform(tree)
        except exceptions.UnexpectedToken:
            print("{} Syntax Error".format(PROMPT))
            input_generator = get_prompt_input()  # reset buffered input


if __name__ == "__main__":
    with open('grammar.lark') as file:
        sql_parser = Lark(file.read(), start="command", lexer="basic")

    transformer = MyTransformer()

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
