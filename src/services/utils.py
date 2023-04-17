import ast
from typing import Union


def to_str(s: Union[str, set]) -> str:
    return str(s) if isinstance(s, set) else s


def to_set(string: Union[str, set]) -> set:
    if isinstance(string, set):
        return string
    else:
        data = ast.literal_eval(string.decode('utf-8'))
        flat_data = [item for sublist in data for item in (
            sublist if isinstance(sublist, list) else [sublist]
        )]
        return set(flat_data)
