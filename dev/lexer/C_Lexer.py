import sys
from pathlib import Path
try:
    from .lexer import Lexer
except ImportError:
    from lexer import Lexer


DEFAULT_INPUT_PATH = str(Path(__file__).resolve().parents[2] / "input.c")


def tokenize_source(source_code):
    lexer = Lexer(source_code)
    return lexer.tokenize()


def tokenize_file(file_path=DEFAULT_INPUT_PATH):
    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()
    return tokenize_source(source)


def main():
    tokens = tokenize_file()
    print(f"{'Line':<4} {'Type':<20} Value")
    print("-" * 40)
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
