from lark.lexer import Token
from typing import List, Optional, Tuple, Union

class Symbol:
    def __init__(self, name: str, kind: str, type: Optional[str], value: Optional[Union[float, int]]=None, size: Optional[int]=None, declared_at: Optional[Tuple[int, int]]=None) -> None:
        self.name = name
        self.kind = kind
        self.type = type
        self.value = value
        self.size = size
        self.declared_at = declared_at
        self.initialized = False


class SymbolTable:
    def __init__(self) -> None:
        self._symbols = {}
        self._errors = []

    def add_error(self, message: str, line: Optional[int]=None, column: Optional[int]=None) -> None:
        location = f" at line {line}, column {column}" if line and column else ""
        self._errors.append(f"Semantic Error{location}: {message}")

    def has_errors(self) -> bool:
        return len(self._errors) > 0

    def get_errors(self) -> List[str]:
        return self._errors

    def _check_identifier_rules(self, name: str, line: int, column: int) -> bool:
        """Checks MiniSoft specific identifier rules."""
        if len(name) > 14:
            self.add_error(
                f"Identifier '{name}' exceeds maximum length of 14 characters.",
                line,
                column,
            )
            return False
        if name.endswith("_"):
            self.add_error(
                f"Identifier '{name}' cannot end with an underscore.", line, column
            )
            return False
        if "__" in name:
            self.add_error(
                f"Identifier '{name}' cannot contain consecutive underscores.",
                line,
                column,
            )
            return False
        # Rule: Starts with a letter, contains letters, digits, _ is handled by regex
        return True

    def insert(self, name: str, kind: str, type: Optional[str], value: Optional[Union[float, int]]=None, size: Optional[int]=None, meta: Optional[Token]=None) -> None:
        line = getattr(meta, "line", None)
        column = getattr(meta, "column", None)

        if not self._check_identifier_rules(name, line, column):
            return  # Don't insert invalid identifiers

        if name in self._symbols:
            prev_decl = self._symbols[name].declared_at
            prev_loc = (
                f"at line {prev_decl[0]}, column {prev_decl[1]}" if prev_decl else ""
            )
            self.add_error(
                f"Identifier '{name}' already declared {prev_loc}.", line, column
            )
        else:
            symbol = Symbol(name, kind, type, value, size, declared_at=(line, column))
            self._symbols[name] = symbol
            print(
                f"DEBUG: Inserted '{name}' ({kind}, {type}, val={value}, size={size})"
            )

    def lookup(self, name: str, meta: Optional[Token]=None) -> Optional[Symbol]:
        line = getattr(meta, "line", None)
        column = getattr(meta, "column", None)
        symbol = self._symbols.get(name)
        if symbol is None:
            self.add_error(f"Identifier '{name}' not declared.", line, column)
            return None
        return symbol
