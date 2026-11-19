from json import load


def open_json(path: str):
    with open(path, "r") as file:
        content = load(file)
    return content
        
def open_file(path: str, newline_separator: bool = False) -> str:
    with open(path) as file:
        content = file.read()
    return content