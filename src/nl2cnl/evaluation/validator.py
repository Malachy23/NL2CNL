from functools import cache
from pathlib import Path

from lark import Lark, LarkError


@cache
def _parser(path: Path) -> Lark:
    # Earley instead of LALR: LALR's lexer splits multi-word literals ("of the", "at least")
    # and rejects valid sentences. The parser is built once per grammar file.
    return Lark.open(str(path), parser="earley")


def is_syntax_valid(text: str, grammar_path: Path = Path("grammar.lark")) -> bool:
    """Returns True if <text> is correctly parsed by the Lark grammar in <grammar_path>"""
    try:
        _parser(Path(grammar_path)).parse(text)
        return True
    except LarkError:
        return False
