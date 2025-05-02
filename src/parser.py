import sys
from lark import Lark, exceptions
from lark.tree import Tree


# -- Lexical and Syntax Analysis --
def parser(filename: str) -> Tree:
    # Read the grammar from the file
    try:
        with open("src/minisoft.lark", "r") as f:
            grammar = f.read()
    except FileNotFoundError:
        print("Error: Grammar file 'minisoft.lark' not found.")
        sys.exit(1)

    # Read the source code from the file
    try:
        with open(filename, "r") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Source file '{filename}' not found.")
        sys.exit(1)

    parser = Lark(
        grammar, start="program", parser="lalr", propagate_positions=True
    )  # Use LALR for speed, propagate positions for errors
    try:
        print(f"Parsing '{filename}'...")
        parse_tree = parser.parse(source_code)
        print("Parsing successful.")
        return parse_tree

    except exceptions.UnexpectedCharacters as e:
        print("\\n--- Lexical Error ---")
        print(
            f"Unexpected characters: '{source_code[e.pos_in_stream]}' at position {e.pos_in_stream}"
        )
        print(f"At line {e.line}, column {e.column}")
        context = source_code.splitlines()[e.line - 1]
        print(f"Context: {context}")
        print(" " * (len("Context: ") + e.column - 1) + "^")
        sys.exit(1)
    except exceptions.UnexpectedToken as e:
        print("\\n--- Syntax Error ---")
        print(f"Unexpected token: '{e.token}'")
        print(f"Expected one of: {e.expected}")
        print(f"At line {e.line}, column {e.column}")
        context = source_code.splitlines()[e.line - 1]
        print(f"Context: {context}")
        print(" " * (len("Context: ") + e.column - 1) + "^")
        sys.exit(1)
    except exceptions.LarkError as e:
        print("\\n--- Parsing Error ---")
        print(e)
        sys.exit(1)
