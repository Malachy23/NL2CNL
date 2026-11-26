from functools import cache

from lark import Lark, LarkError


@cache
def _parser(path: str) -> Lark:
    return Lark.open(path, parser="earley")

def is_syntax_valid(text: str, lark_path: str = "grammar.lark") -> bool:
    """Returns True if <text> is correctly parsed by Lark parser with specified <lark_path> file"""
    try:
        _parser(lark_path).parse(text)
        return True
    except LarkError:
        return False