import sys
from pathlib import Path

try:
	from dev.lexer import tokenize_file, tokenize_source
	from .parser import Parser
except ImportError:
	root = Path(__file__).resolve().parents[2]
	sys.path.insert(0, str(root))
	from dev.lexer import tokenize_file, tokenize_source
	from parser import Parser


DEFAULT_INPUT_PATH = str(Path(__file__).resolve().parents[2] / "input.c")


def parse_tokens(tokens):
	parser = Parser(tokens)
	return parser.parse()


def parse_source(source_code):
	tokens = tokenize_source(source_code)
	return parse_tokens(tokens)


def parse_file(file_path=DEFAULT_INPUT_PATH):
	tokens = tokenize_file(file_path)
	return parse_tokens(tokens)


def validate_tokens(tokens):
	try:
		parse_tokens(tokens)
		return True
	except SyntaxError:
		return False


def validate_source(source_code):
	try:
		parse_source(source_code)
		return True
	except SyntaxError:
		return False


def validate_file(file_path=DEFAULT_INPUT_PATH):
	try:
		parse_file(file_path)
		return True
	except SyntaxError:
		return False


def main():
	print(validate_file())


if __name__ == "__main__":
	main()
