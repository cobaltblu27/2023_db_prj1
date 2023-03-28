import sys
from lark import Lark, Transformer, ParseTree

PROMPT = "DB_2016-19965> "


class MyTransformer(Transformer):
    def create_table_query(self, items):
        pass
        # implemet here

    def drop_table_query(self, items):
        pass
        # implemet here
    
    def exit(self):
        sys.exit()


def get_prompt_input() -> str:
    str_input: str = input(PROMPT)
    while (str_input[-1] != ';'):
        next_line: str = input()
        str_input += " " + next_line
    return str_input


def prompt(parser: Lark, transformer: Transformer):
    while(1):
        query_str = get_prompt_input()
        output: ParseTree = parser.parse(query_str)
        # TODO:
        print("{} {}".format(PROMPT, output.pretty()))
        transformer.transform(output)


if __name__ == "__main__":
    with open('grammar.lark') as file:
        sql_parser = Lark(file.read(), start="command", lexer="basic")

    transformer = MyTransformer()
    _test = True
    if (_test):
        output: ParseTree = sql_parser.parse("select ID from student;")
        print("----------Parsed result----------")
        print(output.pretty())

        transformer.transform(output)
    else:
        prompt(sql_parser, transformer)

