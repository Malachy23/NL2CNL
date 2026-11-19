def open_file(path: str, newline_separator: bool = False) -> str:
    with open(path) as content:
        return content.read()