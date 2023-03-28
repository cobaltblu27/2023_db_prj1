from lark import Lark, Transformer, ParseTree


class MyTransformer(Transformer):
    def create_table_query(self, items):
        pass
        # implemet here

    def drop_table_query(self, items):
        pass
        # implemet here


if __name__ == "__main__":
    with open('grammar.lark') as file:
        sql_parser = Lark(file.read(), start="command", lexer="basic")

    # store parsed output
    output: ParseTree = sql_parser.parse("select ID from student;")
    print("----------Parsed result----------")
    print(output.pretty())

    MyTransformer().transform(output)
