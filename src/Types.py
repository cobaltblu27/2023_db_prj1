from typing import List, Literal, TypedDict, Union, Dict, Optional

AttributeType = Literal["int", "char", "date"]
Constraints = Literal["non-null", "p_key", "f_key"]


class ColumnSpec(TypedDict):
    type: AttributeType
    length: Union[None, int]
    non_null: bool


class ForeignKey(TypedDict):
    columns: List[str]
    table: str
    ref_columns: List[str]


class KeySpec(TypedDict):
    primary_key: List[str]
    foreign_key: List[ForeignKey]


class Alias(TypedDict):
    name: str
    alias: Optional[str]


ColumnDict = Dict[str, ColumnSpec]
ColumnValue = Dict[str, Union[int, str]]
