import json
from lark import Tree, Token
from typing import List, Union, Literal

import lark


def search_item_value(items, data_name: str):
    for item in items:
        if isinstance(item, lark.Tree):
            res = list(item.find_data(data_name))
            if len(res) > 0:
                children = res[0].children
                return children[0] if len(children) > 0 else None
    return None


def search_item(items, data_name: str):
    for item in items:
        if isinstance(item, lark.Tree):
            res = list(item.find_data(data_name))
            if len(res) > 0:
                return res[0]
    return None


def search_children(tree: Tree, keyword: str, type: Literal["tree", "token"] = "tree") -> List[Union[Tree, Token]]:
    def pred(t):
        if type == "tree":
            return isinstance(t, Tree) and t.data == keyword
        else:
            return isinstance(t, Token) and t.value == keyword
    return list(filter(pred, tree.children))


# where_clause : WHERE boolean_exp
# boolean_expr : boolean_term (OR boolean_term)*
# boolean_term : boolean_factor (AND boolean_factor)*
# boolean_factor : [NOT] boolean_test
# boolean_test : predicate
#              | parenthesized_boolean_expr
# parenthesized_boolean_expr : LP boolean_expr RP
# predicate : comparison_predicate
#           | null_predicate
# comparison_predicate : comp_operand comp_op comp_operand
# comp_operand : comparable_value
#              | [table_name "."] column_name
# comparable_value : INT | STR | DATE
# null_predicate : [table_name "."] column_name null_operation
# null_operation : IS [NOT] NULL
def bool_test_rec(row: object, bool_tree: Tree) -> bool:
    # input: boolean_expr | boolean_term | boolean_factor
    # print(bool_tree.data)
    if bool_tree.data == "boolean_expr":
        # or chain
        terms = search_children(bool_tree, "boolean_term")
        return any(map(lambda term: bool_test_rec(row, term), terms))
    elif bool_tree.data == "boolean_term":
        # and chain
        terms = search_children(bool_tree, "boolean_factor")
        return all(map(lambda term: bool_test_rec(row, term), terms))
    elif bool_tree.data == "boolean_factor":
        not_predicate = bool_tree.children[0] is not None
        test = search_children(bool_tree, "boolean_test")[0]
        result = bool_judge_predicate(row, test)
        return not result if not_predicate else result
    return True


def bool_judge_predicate(row, boolean_test: Tree):
    parenthesis = search_children(boolean_test, "parenthesized_boolean_expr")
    if len(parenthesis) > 0:
        expr = search_children(parenthesis[0], "boolean_expr")[0]
        return bool_test_rec(row, expr)
    # comparison_predicate | null_predicate
    predicate: Tree = boolean_test.children[0].children[0]
    if predicate.data == "comparison_predicate":
        print(predicate.pretty())
        return True
    else:
        return True


def where_predicate(row: object, where_clause: Tree) -> bool:
    # print(where_clause.pretty('-'))
    # where starts with boolean_expr
    boolean_expr = search_children(where_clause, "boolean_expr")
    return bool_test_rec(row, boolean_expr[0])
