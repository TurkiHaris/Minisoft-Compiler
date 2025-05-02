import sys
from lark import exceptions
from src.semantic_analyzer import SemanticAnalyzer, get_meta
from src.parser import parser


def main(filename):
    # --- 1. Parsing (Lexical and Syntax Analysis) ---
    print(f"Compiling '{filename}'...")
    parse_tree = None
    parse_tree = parser(filename)
    if parse_tree is None:
        print("Error: Parsing failed. No parse tree generated.")
        sys.exit(1)
    # --- 2. Semantic Analysis ---
    print("\nPerforming semantic analysis...")
    analyzer = SemanticAnalyzer()
    try:
        symbol_table_result = analyzer.transform(parse_tree)
        if symbol_table_result.has_errors():
            print("\n--- Semantic Errors Found ---")
            for error in symbol_table_result.get_errors():
                print(error)
            sys.exit(1)
        else:
            print("Semantic analysis successful. No errors detected.")
            # Print the symbol table
            print("--- MiniSoft Compiler ---")
            print("Authors: TURKI HARIS & ZITOUNI OUSSAMA")
            print("-------------------------")
            print("\n--- Final Symbol Table ---")
            print(
                "Name".ljust(15)
                + "| Kind".ljust(12)
                + "| Type".ljust(8)
                + "| Value".ljust(12)
                + "| Size".ljust(8)
                + "| Location"
            )
            print("-" * 70)
            for name, symbol in symbol_table_result._symbols.items():
                kind_str = str(symbol.kind) if symbol.kind is not None else "None"
                type_str = str(symbol.type) if symbol.type is not None else "None"
                value_str = str(symbol.value) if symbol.value is not None else "None"
                size_str = str(symbol.size) if symbol.size is not None else "None"
                loc_str = (
                    f"line {symbol.declared_at[0]}, col {symbol.declared_at[1]}"
                    if symbol.declared_at
                    else "N/A"
                )
                print(
                    f"{name.ljust(15)}| {kind_str.ljust(10)}| {type_str.ljust(6)}| {value_str.ljust(10)}| {size_str.ljust(6)}| {loc_str}"
                )

    except exceptions.VisitError as e:
        print("\n--- Error during Semantic Analysis ---")
        print(f"Error occurred near: {e.obj}")
        print(f"Original error: {e.orig_exc}")
        meta = get_meta(e.obj)
        if meta:
            print(f"Approximate location: line {meta.line}, column {meta.column}")
        import traceback

        print("\n--- Traceback for Original Error ---")
        traceback.print_exception(
            type(e.orig_exc), e.orig_exc, e.orig_exc.__traceback__
        )
        print("------------------------------------")
        sys.exit(1)

    print(f"\nCompilation check finished successfully for '{filename}'.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <source_file.ms>")
        sys.exit(1)
    source_file = sys.argv[1]
    main(source_file)
