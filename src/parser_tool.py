from lark import Tree, Token
from typing import List, Union, Literal, Dict, Tuple
from datetime import date
import lark

from src.Types import Alias, AttributeType, ColumnValue
from src.errors import WhereIncomparableError, SqlException
from src.tools import trim_str_colons


def parse_type(col_type: str) -> AttributeType:
    type_upper = col_type.upper()
    if type_upper == "STR":
        return "char"
    if type_upper == "DATE":
        return "date"
    if type_upper == "INT":
        return "int"
    raise SqlException


def search_item_value(items: Union[object, list[object]], data_name: str):
    if not isinstance(items, list):
        items = [items]
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
def bool_test_rec(
        row: ColumnValue,
        bool_tree: Tree,
        aliases: List[Alias],
        column_types: Dict[str, AttributeType]
) -> bool:
    # input: boolean_expr | boolean_term | boolean_factor
    if bool_tree.data == "boolean_expr":
        # or chain
        terms = search_children(bool_tree, "boolean_term")
        return any(map(
            lambda term: bool_test_rec(row, term, aliases, column_types),
            terms
        ))
    elif bool_tree.data == "boolean_term":
        # and chain
        terms = search_children(bool_tree, "boolean_factor")
        return all(map(
            lambda term: bool_test_rec(row, term, aliases, column_types),
            terms
        ))
    elif bool_tree.data == "boolean_factor":
        not_predicate = bool_tree.children[0] is not None
        test = search_children(bool_tree, "boolean_test")[0]
        result = bool_judge_predicate(row, test, aliases, column_types)
        return not result if not_predicate else result
    return True


def bool_judge_predicate(
        row, boolean_test: Tree, aliases: List[Alias],
        column_types: Dict[str, AttributeType]
):
    parenthesis = search_children(boolean_test, "parenthesized_boolean_expr")
    if len(parenthesis) > 0:
        expr = search_children(parenthesis[0], "boolean_expr")[0]
        return bool_test_rec(row, expr, aliases, column_types)
    # comparison_predicate | null_predicate
    predicate: Tree = boolean_test.children[0].children[0]
    if predicate.data == "comparison_predicate":
        operands = list(predicate.find_data("comp_operand"))
        op = list(predicate.find_data("comp_op"))[0] \
            .children[0].value
        l_type, l_val = fetch_type_value(row, operands[0], aliases, column_types)
        r_type, r_val = fetch_type_value(row, operands[1], aliases, column_types)
        if l_type != r_type:
            raise WhereIncomparableError

        # print("{}: {} '{}' {}".format(l_type, l_val, op, r_val))
        if op == ">":
            return l_val > r_val
        if op == ">=":
            return l_val >= r_val
        if op == "=":
            return l_val == r_val
        if op == "<=":
            return l_val <= r_val
        if op == "<":
            return l_val < r_val
        if op == "!=":
            return l_val != r_val
        raise SqlException
    else:
        _, null_operand = fetch_type_value(row, predicate, aliases, column_types)
        not_comp = len(list(predicate.find_pred(
            lambda t: t.data == "null_operation" and t.children[1] is not None
        ))) > 0
        return null_operand is not None if not_comp else null_operand is None


def fetch_type_value(
        row: ColumnValue, operand: Tree, aliases: List[Alias],
        column_types: Dict[str, AttributeType]
) -> Tuple[AttributeType, Union[str, int, date, None]]:
    comparable_value = list(operand.find_data("comparable_value"))
    if len(comparable_value) > 0:
        op_type = comparable_value[0].children[0].type
        value = comparable_value[0].children[0].value
        if op_type == "STR":
            value = trim_str_colons(value)
        elif op_type == "DATE":
            [y, m, d] = map(lambda s: int(s), value.split("-"))
            value = date(y, m, d)
        return parse_type(op_type), value

    target_table_name_value = search_item_value(operand, "table_name")
    target_alias = next(
        filter(
            lambda t: t["alias"] == target_table_name_value,
            aliases
        ), None
    )
    target_table_name = target_alias["name"] if target_alias is not None else None
    target_column_name = search_item_value(operand, "column_name")

    def filter_key(k: str):
        [table, col] = k.split(".")[0:2]
        if target_column_name != col:
            return False
        if target_table_name is None:
            return True
        return target_table_name == table

    key = next(filter(filter_key, column_types.keys()), None)
    column_type = column_types[key]
    value = row[key] if key in row else None
    if column_type == "date" and value is not None:
        [y, m, d] = map(lambda s: int(s), value.split("-"))
        value = date(y, m, d)
    return column_type, value


def where_predicate(
        row: ColumnValue, where_clause: Tree, aliases: List[Alias],
        column_types: Dict[str, AttributeType]
) -> bool:
    # where starts with boolean_expr
    boolean_expr = search_children(where_clause, "boolean_expr")
    return bool_test_rec(row, boolean_expr[0], aliases, column_types)


# type check
