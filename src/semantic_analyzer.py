from lark import Transformer, Token, Tree
from src.symbol_table import SymbolTable
import lark.lexer
import lark.tree
from typing import Any, Dict, List, Optional, Union


def get_meta(node: Any) -> Optional[Union[lark.tree.Meta, lark.lexer.Token]]:
    """
    Extracts metadata (line and column information) from an AST node or token.

    This helper function recursively searches for metadata in a parse tree node or token.

    Args:
        node: A Token, Tree, or other node from the parse tree

    Returns:
        The Token object or metadata containing line and column information, or None if not found
    """
    if isinstance(node, Token):
        return node
    elif hasattr(node, "meta"):
        return node.meta
    elif hasattr(node, "children") and node.children:
        for child in node.children:
            if child is not node:
                meta = get_meta(child)
                if meta:
                    return meta
    return None


class SemanticAnalyzer(Transformer):
    """
    Semantic analyzer for the MiniSoft language.

    This class performs static semantic analysis on the AST produced by the parser.
    It checks for type correctness, symbol usage, array bounds, and other semantic constraints.
    It transforms the parse tree into a symbol table containing all declarations and reports
    any semantic errors found during the analysis.

    The analyzer implements the visitor pattern through Lark's Transformer interface,
    with methods named after grammar rules that are called when visiting corresponding nodes.

    Attributes:
        symbol_table: A SymbolTable instance to track declarations and report errors
    """

    def __init__(self, visit_tokens: bool=True) -> None:
        """
        Initialize the semantic analyzer.

        Args:
            visit_tokens: Whether to visit token nodes in the parse tree
        """
        super().__init__(visit_tokens=visit_tokens)
        self.symbol_table = SymbolTable()

    # Token handlers - convert tokens to Python values
    def INT(self, token:     lark.lexer.Token) ->     lark.lexer.Token:
        return token

    def FLOAT(self, token:     lark.lexer.Token) ->     lark.lexer.Token:
        return token

    def IDENTIFIER(self, token:     lark.lexer.Token) ->     lark.lexer.Token:
        return token

    def INTEGER(self, token:     lark.lexer.Token) ->     lark.lexer.Token:
        return token

    def FLOAT_VAL(self, token:     lark.lexer.Token) ->     lark.lexer.Token:
        return token

    def SIGN(self, token:     lark.lexer.Token) ->     lark.lexer.Token:
        return token

    def STRING(self, token:     lark.lexer.Token) ->     lark.lexer.Token:
        return token

    def _find_item(self, items: List[Any], expected_type_or_value: str) -> Optional[    lark.lexer.Token]:
        """
        Find a token with a specific type or value in a list of items.

        Args:
            items: List of parse tree items to search through
            expected_type_or_value: The token type or value to look for

        Returns:
            The first matching Token or None if not found
        """
        for item in items:
            if isinstance(item, Token):
                if (
                    item.type == expected_type_or_value
                    or item.value == expected_type_or_value
                ):
                    return item
        return None

    def _find_result(self, items: List[Union[List[    lark.lexer.Token], Dict[str, Union[int,     lark.lexer.Token, str]], Dict[str, Optional[Union[str,     lark.lexer.Token]]],     lark.lexer.Token, Dict[str, Union[str, float,     lark.lexer.Token]]]], expected_key: str="type", is_list: bool=False) -> Union[Dict[str, Optional[Union[str,     lark.lexer.Token]]], Dict[str, Union[str, float,     lark.lexer.Token]], List[    lark.lexer.Token], Dict[str, Union[int,     lark.lexer.Token, str]]]:
        """
        Find a dictionary result with a specific key or a list in a collection of items.

        Args:
            items: List of items to search through
            expected_key: The dictionary key to look for
            is_list: If True, look for a list instead of a dictionary

        Returns:
            The matching dictionary or list, or None if not found
        """
        for item in items:
            if is_list and isinstance(item, list):
                return item
            if not is_list and isinstance(item, dict) and expected_key in item:
                return item
        return None

    def _find_all_results(self, items: List[Any], expected_key: str="type") -> List[Dict[str, Any]]:
        """
        Find all dictionaries with a specific key in a collection of items.

        Args:
            items: List of items to search through
            expected_key: The dictionary key to look for

        Returns:
            List of all matching dictionaries
        """
        if expected_key is None:
            return []
        results = []
        for item in items:
            if isinstance(item, dict) and expected_key in item:
                results.append(item)
        return results

    def _find_all_tokens(self, items: List[    lark.lexer.Token], expected_type: str) -> List[    lark.lexer.Token]:
        """
        Find all tokens of a specific type in a collection of items.

        Args:
            items: List of items to search through
            expected_type: The token type to look for

        Returns:
            List of all matching tokens
        """
        tokens = []
        for item in items:
            if isinstance(item, Token) and item.type == expected_type:
                tokens.append(item)
        return tokens

    def program(self, items: List[Union[    lark.lexer.Token,     lark.tree.Tree]]) -> SymbolTable:
        """
        Process the program node, which is the root of the AST.

        Registers the program name in the symbol table and performs semantic analysis
        on all declarations and statements in the program.

        Args:
            items: List of child nodes from the parse tree

        Returns:
            The populated symbol table with all declarations and any semantic errors
        """
        prog_name_token = self._find_item(items, "IDENTIFIER")
        if prog_name_token:
            self.symbol_table.insert(
                prog_name_token.value, "program", None, meta=prog_name_token
            )
        else:
            line, col = (1, 1)
            meta = get_meta(items[0] if items else None)
            if meta:
                line, col = meta.line, meta.column
            self.symbol_table.add_error(
                "Internal error: Could not find program name.", line, col
            )
        return self.symbol_table

    def identifier_list(self, items: List[    lark.lexer.Token]) -> List[    lark.lexer.Token]:
        """
        Process a list of identifiers used in variable declarations.

        Args:
            items: List of identifier tokens

        Returns:
            List of identifier tokens
        """
        id_tokens = self._find_all_tokens(items, "IDENTIFIER")
        print(f"DEBUG: identifier_list returning tokens: {id_tokens}")
        return id_tokens

    def basic_type(self, items: List[    lark.lexer.Token]) -> Dict[str, Optional[Union[str,     lark.lexer.Token]]]:
        """
        Process a basic type (Int or Float) declaration.

        Args:
            items: List containing a single type token

        Returns:
            Dictionary with type information: {'type': type_name, 'size': None, 'meta': token}
        """
        type_token = items[0] if items else None
        print(f"DEBUG: basic_type received items: {items}")
        if isinstance(type_token, Token) and type_token.type in ("INT", "FLOAT"):
            return {"type": type_token.value, "size": None, "meta": type_token}
        else:
            print(f"DEBUG: basic_type failed find type token in items: {items}")
            self.symbol_table.add_error("Internal error: Failed processing basic type.")
            return {"type": "ErrorType", "size": None, "meta": get_meta(type_token)}

    def positive_integer(self, items: List[    lark.lexer.Token]) -> Dict[str, Union[int,     lark.lexer.Token, str]]:
        """
        Process a positive integer used for array size declarations.

        Validates that the integer value is a valid array size (must be positive).

        Args:
            items: List containing a single INTEGER token

        Returns:
            Dictionary with value information: {'value': int_value, 'meta': token, 'type': 'Int'}
        """
        print(f"DEBUG: positive_integer received items: {items}")
        token = items[0] if items else None
        if isinstance(token, Token) and token.type == "INTEGER":
            return {"value": int(token.value), "meta": token, "type": "Int"}
        else:
            print(f"DEBUG: positive_integer expected INTEGER token, got {items}")
            self.symbol_table.add_error(
                "Internal error: Expected integer value for size."
            )
            return {"value": 0, "meta": None, "type": "ErrorType"}

    def type_specifier(self, items):
        """
        Process a type specifier, which can be either a basic type or array type.

        Args:
            items: List containing a single type information dictionary

        Returns:
            Dictionary with type information
        """
        print(f"DEBUG: type_specifier received items: {items}")
        result = items[0] if items else None
        if isinstance(result, dict):
            return result
        print(f"DEBUG: type_specifier did not receive dict result: {items}")
        self.symbol_table.add_error("Internal error processing type specifier.")
        return {"type": "ErrorType", "size": None}

    def array_specifier(self, items: List[Dict[str, Optional[Union[str,     lark.lexer.Token, int]]]]) -> Dict[str, Union[int,     lark.lexer.Token, str]]:
        """
        Process an array type specifier: [basic_type; size]

        Validates that the array size is positive and creates the array type information.

        Args:
            items: List containing basic type information and size information

        Returns:
            Dictionary with array type information: {'type': element_type, 'size': array_size, 'meta': token}
        """
        print(f"DEBUG: array_specifier received items: {items}")
        basic_type_info = self._find_result(items, "type")
        size_info = self._find_result(items, "value")

        if not basic_type_info or not size_info:
            print(
                f"DEBUG: array_specifier failed find results. basic={basic_type_info}, size={size_info}"
            )
            self.symbol_table.add_error(
                "Internal error processing array specifier structure."
            )
            return {"type": "ErrorType", "size": None}

        if (
            basic_type_info.get("type") == "ErrorType"
            or size_info.get("type") == "ErrorType"
        ):
            return {"type": "ErrorType", "size": None}

        type_name = basic_type_info["type"]
        size_val = size_info["value"]
        size_token_meta = size_info["meta"]

        if not size_token_meta:
            meta = basic_type_info.get("meta")
            line = getattr(meta, "line", "?")
            col = getattr(meta, "column", "?")
            self.symbol_table.add_error(
                f"Internal error: Missing metadata for array size '{size_val}'.",
                line,
                col,
            )
            return {"type": "ErrorType", "size": None}

        if size_val <= 0:
            self.symbol_table.add_error(
                f"Array size must be positive integer, got '{size_val}'.",
                size_token_meta.line,
                size_token_meta.column,
            )
            return {"type": "ErrorType", "size": None, "meta": size_token_meta}

        return {
            "type": type_name,
            "size": size_val,
            "meta": basic_type_info.get("meta"),
        }

    def constant_value(self, items):
        """
        Process a constant value (signed integer or float).

        Args:
            items: List containing a single value information dictionary

        Returns:
            Dictionary with value information
        """
        print(f"DEBUG: constant_value received items: {items}")
        result = items[0] if items else None
        if isinstance(result, dict):
            return result
        print(f"DEBUG: constant_value did not receive dict result: {items}")
        self.symbol_table.add_error("Internal error processing constant value.")
        return {"type": "ErrorType", "value": None, "meta": None}

    def signed_integer(self, items: List[    lark.lexer.Token]) -> Dict[str, Union[int,     lark.lexer.Token, str]]:
        """
        Process a signed integer literal.

        Handles optional sign and parentheses, converting the token to an integer value.

        Args:
            items: List containing INTEGER token and optional SIGN and parentheses tokens

        Returns:
            Dictionary with integer value information: {'type': 'Int', 'value': int_value, 'meta': token}
        """
        print(f"DEBUG: signed_integer received items: {items}")
        sign = 1
        val_token = self._find_item(items, "INTEGER")
        sign_token = self._find_item(items, "SIGN")
        paren_token = self._find_item(items, "(")

        if not val_token:
            print("DEBUG: signed_integer failed find INTEGER token.")
            meta = get_meta(items[0] if items else None)
            self.symbol_table.add_error(
                "Internal error: Invalid integer literal structure.",
                getattr(meta, "line", "?"),
                getattr(meta, "column", "?"),
            )
            return {"type": "ErrorType", "value": None, "meta": meta}

        if paren_token:
            try:
                val_pos = items.index(val_token)
                if sign_token:
                    sign_pos = items.index(sign_token)
                    if sign_pos > val_pos:
                        print("DEBUG: signed_integer token order issue in parens.")
                        self.symbol_table.add_error(
                            "Internal error: Invalid signed integer structure.",
                            val_token.line,
                            val_token.column,
                        )
                        return {"type": "ErrorType", "value": None, "meta": val_token}
            except ValueError:
                self.symbol_table.add_error(
                    "Internal error: Parsing signed integer.",
                    val_token.line,
                    val_token.column,
                )
                return {"type": "ErrorType", "value": None, "meta": val_token}

        if sign_token and sign_token.value == "-":
            sign = -1

        value = sign * int(val_token.value)
        return {"type": "Int", "value": value, "meta": val_token}

    def signed_float(self, items: List[    lark.lexer.Token]) -> Dict[str, Union[str, float,     lark.lexer.Token]]:
        """
        Process a signed float literal.

        Handles optional sign and parentheses, converting the token to a float value.

        Args:
            items: List containing FLOAT_VAL token and optional SIGN and parentheses tokens

        Returns:
            Dictionary with float value information: {'type': 'Float', 'value': float_value, 'meta': token}
        """
        print(f"DEBUG: signed_float received items: {items}")
        sign = 1
        val_token = self._find_item(items, "FLOAT_VAL")
        sign_token = self._find_item(items, "SIGN")
        paren_token = self._find_item(items, "(")

        if not val_token:
            print("DEBUG: signed_float failed find FLOAT_VAL token.")
            meta = get_meta(items[0] if items else None)
            self.symbol_table.add_error(
                "Internal error: Invalid float literal structure.",
                getattr(meta, "line", "?"),
                getattr(meta, "column", "?"),
            )
            return {"type": "ErrorType", "value": None, "meta": meta}

        if paren_token:
            try:
                val_pos = items.index(val_token)
                if sign_token:
                    sign_pos = items.index(sign_token)
                    if sign_pos > val_pos:
                        print("DEBUG: signed_float token order issue in parens.")
                        self.symbol_table.add_error(
                            "Internal error: Invalid signed float structure.",
                            val_token.line,
                            val_token.column,
                        )
                        return {"type": "ErrorType", "value": None, "meta": val_token}
            except ValueError:
                self.symbol_table.add_error(
                    "Internal error: Parsing signed float.",
                    val_token.line,
                    val_token.column,
                )
                return {"type": "ErrorType", "value": None, "meta": val_token}

        if sign_token and sign_token.value == "-":
            sign = -1

        value = sign * float(val_token.value)
        return {"type": "Float", "value": value, "meta": val_token}

    # --- Declarations ---
    def variable_declaration(self, items: List[Union[List[    lark.lexer.Token], Dict[str, Optional[Union[str,     lark.lexer.Token]]], Dict[str, Union[int,     lark.lexer.Token, str]]]]) -> None:
        """
        Process a variable declaration statement: 'let id1, id2, ... : type;'

        Extracts identifiers and their type, then registers them in the symbol table.
        Validates that the type is valid and identifiers are unique.

        Args:
            items: List containing identifier list and type information

        Returns:
            None
        """
        print(f"DEBUG: variable_declaration received items: {items}")
        id_list_result = self._find_result(items, is_list=True)
        type_info = self._find_result(items, "type")

        if not isinstance(id_list_result, list) or not isinstance(type_info, dict):
            print(
                f"DEBUG: variable_declaration failed find items. ids={id_list_result}, type={type_info}"
            )
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error processing variable declaration structure."
                )
            return None

        if type_info.get("type") == "ErrorType":
            return None

        kind = "array" if type_info.get("size") is not None else "variable"
        var_type = type_info.get("type")
        if not var_type or var_type == "ErrorType":
            print(f"DEBUG: variable_declaration has invalid type: {var_type}")
            return None

        for id_token in id_list_result:
            if isinstance(id_token, Token) and id_token.type == "IDENTIFIER":
                self.symbol_table.insert(
                    id_token.value,
                    kind,
                    var_type,
                    size=type_info.get("size"),
                    meta=id_token,
                )
            else:
                print(
                    f"DEBUG: variable_declaration expected IDENTIFIER token in list, got: {id_token}"
                )
                self.symbol_table.add_error(
                    "Internal error processing identifier in list."
                )
        return None

    def constant_declaration(self, items: List[Union[    lark.lexer.Token, Dict[str, Optional[Union[str,     lark.lexer.Token]]], Dict[str, Union[int,     lark.lexer.Token, str]], Dict[str, Union[str, float,     lark.lexer.Token]]]]) -> None:
        """
        Process a constant declaration: '@define Const ID : type = value;'

        Validates that the declared type matches the initialization value's type
        and that the constant value is within the valid range for the type.

        Args:
            items: List containing identifier token, type info, and value info

        Returns:
            None
        """
        print(f"DEBUG: constant_declaration received items: {items}")
        const_name_token = self._find_item(items, "IDENTIFIER")
        type_info = self._find_result(items, "type")
        const_val_info = self._find_result(items, "value")

        if not const_name_token or not type_info or not const_val_info:
            print(
                f"DEBUG: constant_declaration failed find items. name={const_name_token}, type={type_info}, val={const_val_info}"
            )
            self.symbol_table.add_error(
                "Internal error processing constant declaration structure."
            )
            return None

        if (
            type_info.get("type") == "ErrorType"
            or const_val_info.get("type") == "ErrorType"
        ):
            print("DEBUG: Error type detected in constant_declaration children")
            return None

        meta = const_name_token
        declared_type = type_info.get("type")
        value_type = const_val_info.get("type")
        value = const_val_info.get("value")

        if declared_type != value_type:
            actual_val_type = const_val_info.get("type", "unknown")
            self.symbol_table.add_error(
                f"Constant '{const_name_token.value}' declared as '{declared_type}' "
                f"but initialized with value of type '{actual_val_type}'.",
                meta.line,
                meta.column,
            )
            self.symbol_table.insert(
                const_name_token.value, "constant", declared_type, value=None, meta=meta
            )
        else:
            if declared_type == "Int":
                if value is None:
                    self.symbol_table.add_error(
                        f"Internal error: Missing value for Int constant '{const_name_token.value}'."
                    )
                elif not (-32768 <= value <= 32767):
                    self.symbol_table.add_error(
                        f"Integer constant '{const_name_token.value}' value '{value}' out of range [-32768, 32767].",
                        meta.line,
                        meta.column,
                    )
                    self.symbol_table.insert(
                        const_name_token.value, "constant", "Int", value=None, meta=meta
                    )
                else:
                    self.symbol_table.insert(
                        const_name_token.value,
                        "constant",
                        "Int",
                        value=value,
                        meta=meta,
                    )
            elif declared_type == "Float":
                if value is None:
                    self.symbol_table.add_error(
                        f"Internal error: Missing value for Float constant '{const_name_token.value}'."
                    )
                else:
                    self.symbol_table.insert(
                        const_name_token.value,
                        "constant",
                        "Float",
                        value=value,
                        meta=meta,
                    )
            else:
                self.symbol_table.add_error(
                    f"Internal error: Unexpected constant type '{declared_type}'."
                )
        return None

    # --- Variable Access ---
    def variable_access(self, items: List[Union[    lark.lexer.Token,     lark.tree.Tree]]) -> Any:
        """
        Process variable access, which can be either an identifier or array access.

        Performs semantic checks:
        - The variable must be declared
        - If array access, the array must be an array type
        - If array access, the index must be of type Int
        - If array access with a constant index, it must be within array bounds

        Args:
            items: List containing either an IDENTIFIER token or array_access Tree

        Returns:
            Dictionary with variable information:
            {'name': name, 'type': type, 'kind': kind, 'is_array_element': bool,
             'index_type': index_type, 'value': value, 'meta': token}
        """
        print(f"DEBUG: variable_access received items: {items}")
        item = items[0] if items else None

        if isinstance(item, Token) and item.type == "IDENTIFIER":
            print(f"DEBUG: variable_access processing IDENTIFIER: {item.value}")
            symbol = self.symbol_table.lookup(item.value, meta=item)
            if not symbol:
                return {"type": "ErrorType", "meta": item, "name": item.value}
            print(f"DEBUG: variable_access looked up {item.value}, found: {symbol}")
            return {
                "name": symbol.name,
                "type": symbol.type,
                "kind": symbol.kind,
                "is_array_element": False,
                "index_type": None,
                "value": symbol.value,
                "meta": item,
            }

        elif isinstance(item, Tree) and item.data == "array_access":
            print(f"DEBUG: variable_access processing array_access Tree: {item}")
            if len(item.children) != 2:
                print("DEBUG: variable_access - Malformed array_access Tree.")
                meta = get_meta(item)
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        "Internal error: Malformed array access structure.",
                        getattr(meta, "line", "?"),
                        getattr(meta, "column", "?"),
                    )
                return {
                    "type": "ErrorType",
                    "meta": meta,
                    "name": "<malformed_array_access>",
                }

            array_name_token = item.children[0]
            index_expr_result = item.children[1]

            if (
                not isinstance(array_name_token, Token)
                or array_name_token.type != "IDENTIFIER"
            ):
                print("DEBUG: variable_access - Array access missing identifier.")
                meta = get_meta(item)
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        "Internal error: Array access missing identifier.",
                        getattr(meta, "line", "?"),
                        getattr(meta, "column", "?"),
                    )
                return {
                    "type": "ErrorType",
                    "meta": meta,
                    "name": "<missing_array_name>",
                }

            if (
                not isinstance(index_expr_result, dict)
                or "type" not in index_expr_result
            ):
                print("DEBUG: variable_access - Invalid array index expression result.")
                meta = get_meta(index_expr_result or item)
                line = getattr(meta, "line", "?")
                col = getattr(meta, "column", "?")
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        "Internal error processing array index.", line, col
                    )
                return {
                    "type": "ErrorType",
                    "meta": meta,
                    "name": array_name_token.value,
                }

            if index_expr_result.get("type") == "ErrorType":
                print("DEBUG: variable_access - ErrorType from index expression.")
                return {
                    "type": "ErrorType",
                    "meta": get_meta(item),
                    "name": array_name_token.value,
                }

            if index_expr_result.get("type") != "Int":
                index_meta = index_expr_result.get("meta", get_meta(item.children[1]))
                line = getattr(index_meta, "line", "?")
                col = getattr(index_meta, "column", "?")
                self.symbol_table.add_error(
                    f"Array index for '{array_name_token.value}' must be Int, got '{index_expr_result.get('type')}'.",
                    line,
                    col,
                )
                return {
                    "type": "ErrorType",
                    "meta": get_meta(item),
                    "name": array_name_token.value,
                }

            symbol = self.symbol_table.lookup(
                array_name_token.value, meta=array_name_token
            )
            if not symbol:
                return {
                    "type": "ErrorType",
                    "meta": array_name_token,
                    "name": array_name_token.value,
                }

            if symbol.kind != "array":
                self.symbol_table.add_error(
                    f"Identifier '{symbol.name}' is not an array.",
                    array_name_token.line,
                    array_name_token.column,
                )
                return None

            if "value" in index_expr_result and index_expr_result["value"] is not None:
                index_value = index_expr_result["value"]
                array_size = symbol.size
                index_meta = index_expr_result.get("meta", get_meta(item.children[1]))
                line = getattr(index_meta, "line", "?")
                col = getattr(index_meta, "column", "?")

                if index_value < 0:
                    self.symbol_table.add_error(
                        f"Array index '{index_value}' cannot be negative for assignment to '{symbol.name}'.",
                        line,
                        col,
                    )
                    return None
                elif index_value >= array_size:
                    self.symbol_table.add_error(
                        f"Array index '{index_value}' out of bounds for assignment to '{symbol.name}' (size {array_size}, valid range [0..{array_size - 1}]).",
                        line,
                        col,
                    )
                    return None

            return {
                "name": symbol.name,
                "type": symbol.type,
                "kind": "variable",
                "is_array_element": True,
                "index_type": "Int",
                "value": None,
                "meta": get_meta(item),
            }

        elif isinstance(item, dict) and "name" in item and "type" in item:
            print(f"DEBUG: variable_access received pre-processed dict: {item}")
            return item

        else:
            print(
                f"DEBUG: variable_access unexpected item: {item} (type: {type(item)})"
            )
            meta = get_meta(item or items)
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error processing variable access structure.",
                    getattr(meta, "line", "?"),
                    getattr(meta, "column", "?"),
                )
            return {
                "type": "ErrorType",
                "meta": meta,
                "name": "<unknown_variable_access>",
            }

    # --- Expressions ---
    def atom(self, items):
        """
        Process an atom, which is the most basic expression element.

        An atom can be a literal value, variable reference, or parenthesized expression.

        Args:
            items: List containing the atom components

        Returns:
            Dictionary with type information and, if available, value
        """
        print(f"DEBUG: atom received items: {items}")
        if not items:
            print("DEBUG: atom received empty items list")
            return {"type": "ErrorType", "meta": None, "value": None}

        result = next(
            (item for item in items if isinstance(item, dict) and "type" in item), None
        )
        print(f"DEBUG: atom processing result: {result} (type: {type(result)})")

        if result:
            if result.get("type") == "ErrorType":
                print("DEBUG: atom propagating ErrorType from child")
            else:
                print(f"DEBUG: atom returning valid result dict: {result}")
            return result
        else:
            print(f"DEBUG: atom did NOT find a result dictionary in items: {items}")
            meta = get_meta(items)
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error: Atom failed to resolve to a typed value.",
                    getattr(meta, "line", "?"),
                    getattr(meta, "column", "?"),
                )
            return {"type": "ErrorType", "meta": meta, "value": None}

    def factor(self, items: List[Any]) -> Dict[str, Any]:
        """
        Process a factor, which can be an atom with an optional unary operator.

        Handles unary operators:
        - Unary plus/minus: Applied to Int or Float operands
        - Logical NOT: Applied to Int operands only

        Args:
            items: List containing operand and optional unary operator

        Returns:
            Dictionary with expression type information
        """
        print(f"DEBUG: factor received items: {items}")
        not_token = self._find_item(items, "NOT")
        sign_token = self._find_item(items, "PLUS") or self._find_item(items, "MINUS")
        operator_token = not_token or sign_token

        operand_node = None
        potential_operand_items = [
            item
            for item in items
            if item not in [not_token, sign_token] and item is not None
        ]

        if len(potential_operand_items) == 1:
            operand_node = potential_operand_items[0]
        elif len(potential_operand_items) > 1:
            dict_item = next(
                (
                    item
                    for item in potential_operand_items
                    if isinstance(item, dict) and "type" in item
                ),
                None,
            )
            if dict_item:
                operand_node = dict_item
            else:
                operand_node = (
                    potential_operand_items[0] if potential_operand_items else None
                )
                print(
                    f"WARN: factor had multiple potential operands, guessing: {operand_node}"
                )

        print(
            f"DEBUG: factor identified tokens: NOT={not_token}, SIGN={sign_token}. Deduced operand_node: {operand_node}"
        )

        operand_result = None
        if isinstance(operand_node, dict) and "type" in operand_node:
            operand_result = operand_node
        elif isinstance(operand_node, Token) and operand_node.type == "IDENTIFIER":
            print(
                f"DEBUG: factor calling variable_access for raw IDENTIFIER: {operand_node}"
            )
            operand_result = self.variable_access([operand_node])
        elif isinstance(operand_node, Tree) and operand_node.data == "array_access":
            print(
                f"DEBUG: factor calling variable_access for raw array_access Tree: {operand_node}"
            )
            operand_result = self.variable_access([operand_node])
        elif isinstance(operand_node, Token) and operand_node.type in (
            "INTEGER",
            "FLOAT_VAL",
        ):
            print(f"DEBUG: factor calling atom for raw literal: {operand_node}")
            operand_result = self.atom([operand_node])
        elif operand_node is not None:
            print(f"DEBUG: factor calling atom for unexpected node: {operand_node}")
            operand_result = self.atom([operand_node])

        print(f"DEBUG: factor operand_result after processing: {operand_result}")

        if operand_result is None:
            print(
                f"DEBUG: factor failed to resolve operand result from node: {operand_node} in items: {items}"
            )
            meta = get_meta(operand_node or items)
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error: Factor could not resolve operand.",
                    getattr(meta, "line", "?"),
                    getattr(meta, "column", "?"),
                )
            return {"type": "ErrorType", "meta": meta}

        if operand_result.get("type") == "ErrorType":
            print(f"DEBUG: factor propagating ErrorType from operand: {operand_result}")
            return operand_result

        op_meta = get_meta(operator_token or operand_result.get("meta"))

        if not_token:
            operand_type = operand_result.get("type")
            if operand_result.get("kind") == "array":
                op_name = operand_result.get("name", "<unknown_array>")
                self.symbol_table.add_error(
                    f"Cannot apply logical NOT '{not_token.value}' directly to array '{op_name}'. Use array element access.",
                    getattr(op_meta, "line", "?"),
                    getattr(op_meta, "column", "?"),
                )
                return {"type": "ErrorType", "meta": op_meta}
            if operand_type != "Int":
                self.symbol_table.add_error(
                    f"Logical NOT '{not_token.value}' requires Int operand, got '{operand_type}'.",
                    getattr(op_meta, "line", "?"),
                    getattr(op_meta, "column", "?"),
                )
                return {"type": "ErrorType", "meta": op_meta}
            print(f"DEBUG: factor applying NOT to {operand_result}")
            return {"type": "Int", "value": None, "meta": op_meta}

        elif sign_token:
            operand_type = operand_result.get("type")
            if operand_result.get("kind") == "array":
                op_name = operand_result.get("name", "<unknown_array>")
                self.symbol_table.add_error(
                    f"Cannot apply unary sign '{sign_token.value}' directly to array '{op_name}'. Use array element access.",
                    getattr(op_meta, "line", "?"),
                    getattr(op_meta, "column", "?"),
                )
                return {"type": "ErrorType", "meta": op_meta}
            if operand_type not in ["Int", "Float"]:
                self.symbol_table.add_error(
                    f"Unary sign '{sign_token.value}' requires Int/Float, got '{operand_type}'.",
                    getattr(op_meta, "line", "?"),
                    getattr(op_meta, "column", "?"),
                )
                return {"type": "ErrorType", "meta": op_meta}

            new_value = None
            op_val = operand_result.get("value")
            if op_val is not None:
                try:
                    new_value = -op_val if sign_token.value == "-" else op_val
                except TypeError:
                    new_value = None

            print(f"DEBUG: factor applying SIGN {sign_token.value} to {operand_result}")
            return {"type": operand_type, "value": new_value, "meta": op_meta}

        else:
            print(
                f"DEBUG: factor returning processed operand result directly: {operand_result}"
            )
            return operand_result

    # --- Assignment ---
    def assignment(self, items: List[Any]) -> None:
        """
        Process an assignment statement: variable_access := expression

        Performs semantic checks:
        - The left-hand side must be a valid variable or array element
        - Cannot assign to a constant
        - Cannot assign to an entire array (must assign to elements)
        - The expression type must be compatible with the variable type
        - Int variables cannot be assigned Float expressions
        - Float variables can be assigned Int expressions (implicit conversion)

        If the assignment involves constant expressions or variables with known values,
        the analyzer will track the value for later constant folding.

        Args:
            items: List containing variable_access, := token, and expression components

        Returns:
            None
        """
        print(f"DEBUG: assignment received items: {items}")
        if not items or len(items) < 2:
            print("DEBUG: assignment received insufficient items")
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error: Assignment missing operands."
                )
            return None

        var_access = items[0]
        var_info = None

        if isinstance(var_access, Token) and var_access.type == "IDENTIFIER":
            symbol = self.symbol_table.lookup(var_access.value, meta=var_access)
            if not symbol:
                return None
            var_info = {
                "name": symbol.name,
                "type": symbol.type,
                "kind": symbol.kind,
                "is_array_element": False,
                "index_type": None,
                "meta": var_access,
            }
        elif isinstance(var_access, Tree) and var_access.data == "array_access":
            array_name_token = var_access.children[0]
            index_expr_result = var_access.children[1]
            if (
                not isinstance(index_expr_result, dict)
                or "type" not in index_expr_result
            ):
                print("DEBUG: assignment - invalid array index expression result")
                meta = (
                    get_meta(var_access.children[1])
                    if len(var_access.children) > 1
                    else get_meta(var_access)
                )
                line = getattr(meta, "line", "?")
                col = getattr(meta, "column", "?")
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        "Internal error processing array index.", line, col
                    )
                return None

            if index_expr_result.get("type") == "ErrorType":
                return None
            if index_expr_result.get("type") != "Int":
                index_meta = index_expr_result.get(
                    "meta", get_meta(var_access.children[1])
                )
                line = getattr(index_meta, "line", "?")
                col = getattr(index_meta, "column", "?")
                self.symbol_table.add_error(
                    f"Array index must be Int, got '{index_expr_result.get('type')}'.",
                    line,
                    col,
                )
                return None

            symbol = self.symbol_table.lookup(
                array_name_token.value, meta=array_name_token
            )
            if not symbol:
                return None
            if symbol.kind != "array":
                self.symbol_table.add_error(
                    f"Identifier '{symbol.name}' is not an array.",
                    array_name_token.line,
                    array_name_token.column,
                )
                return None

            if "value" in index_expr_result and index_expr_result["value"] is not None:
                index_value = index_expr_result["value"]
                array_size = symbol.size
                if not (0 <= index_value < array_size):
                    index_meta = index_expr_result.get(
                        "meta", get_meta(var_access.children[1])
                    )
                    line = getattr(index_meta, "line", "?")
                    col = getattr(index_meta, "column", "?")
                    self.symbol_table.add_error(
                        f"Array index '{index_value}' out of bounds for assignment to '{symbol.name}' (size {array_size}, valid range [0..{array_size - 1}]).",
                        line,
                        col,
                    )
                    return None

            var_info = {
                "name": symbol.name,
                "type": symbol.type,
                "kind": symbol.kind,
                "is_array_element": True,
                "index_type": "Int",
                "meta": get_meta(var_access),
            }
        else:
            print(f"DEBUG: assignment unhandled LHS: {var_access}")
            meta = get_meta(var_access)
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error: Invalid left-hand side in assignment.",
                    getattr(meta, "line", "?"),
                    getattr(meta, "column", "?"),
                )
            return None

        if (
            var_info
            and var_info.get("kind") == "array"
            and not var_info.get("is_array_element")
        ):
            meta = var_info.get("meta")
            self.symbol_table.add_error(
                f"Cannot assign directly to array '{var_info.get('name', '<unknown>')}'. Assign to an element (e.g., array[index] := ...).",
                getattr(meta, "line", "?"),
                getattr(meta, "column", "?"),
            )
            return None

        expr_info = None
        assign_token_index = -1
        for i, item in enumerate(items):
            if isinstance(item, Token) and item.value == ":=":
                assign_token_index = i
                break

        if assign_token_index != -1:
            search_start = assign_token_index + 1
            search_end = len(items)
            for i in range(search_start, len(items)):
                if isinstance(items[i], Token) and items[i].value == ";":
                    search_end = i
                    break
            for i in range(search_start, search_end):
                item = items[i]
                if isinstance(item, dict) and "type" in item:
                    expr_info = item
                    break
        else:
            if len(items) > 1:
                for item in reversed(items[1:]):
                    if isinstance(item, dict) and "type" in item:
                        expr_info = item
                        break

        if not expr_info:
            print(
                f"DEBUG: assignment failed to find expression result dict in items: {items} near assign token index {assign_token_index}"
            )
            expr_part = next(
                (
                    x
                    for x in reversed(items[1:])
                    if not isinstance(x, Token) and x is not None
                ),
                None,
            )
            meta = get_meta(expr_part or items)
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error: Assignment missing expression result.",
                    getattr(meta, "line", "?"),
                    getattr(meta, "column", "?"),
                )
            return None

        if expr_info.get("type") == "ErrorType":
            print("DEBUG: assignment - ErrorType from expression.")
            return None

        if (
            expr_info
            and expr_info.get("kind") == "array"
            and not expr_info.get("is_array_element")
        ):
            target_meta = var_info.get("meta")
            self.symbol_table.add_error(
                f"Cannot assign entire array '{expr_info.get('name', '<unknown>')}' to variable '{var_info.get('name', '<unknown>')}'.",
                getattr(target_meta, "line", "?"),
                getattr(target_meta, "column", "?"),
            )
            return None

        if var_info.get("kind") == "constant":
            meta = var_info.get("meta")
            self.symbol_table.add_error(
                f"Cannot assign to constant '{var_info.get('name', '<unknown>')}'.",
                getattr(meta, "line", "?"),
                getattr(meta, "column", "?"),
            )
            return None

        target_type = var_info.get("type")
        expr_type = expr_info.get("type")
        assign_meta = var_info.get("meta")

        if target_type == "Float" and expr_type == "Int":
            pass
        elif not self._check_type_compatibility(
            target_type, expr_type, assign_meta, allow_float_int=False
        ):
            return None
        elif target_type == "Int" and expr_type == "Float":
            self.symbol_table.add_error(
                f"Cannot assign Float expression to Int variable '{var_info.get('name', '<unknown>')}'",
                getattr(assign_meta, "line", "?"),
                getattr(assign_meta, "column", "?"),
            )
            return None

        if (
            not var_info.get("is_array_element")
            and target_type in ["Int", "Float"]
            and isinstance(expr_info, dict)
        ):
            symbol = self.symbol_table.lookup(var_info["name"])
            if symbol:
                rhs_value = expr_info.get("value")
                rhs_kind = expr_info.get("kind")

                if rhs_value is not None:
                    if target_type == "Int" and isinstance(rhs_value, int):
                        symbol.value = rhs_value
                        print(
                            f"DEBUG: Updated symbol '{symbol.name}' value to literal {symbol.value}"
                        )
                    elif target_type == "Float" and isinstance(rhs_value, (int, float)):
                        symbol.value = float(rhs_value)
                        print(
                            f"DEBUG: Updated symbol '{symbol.name}' value to literal {symbol.value}"
                        )
                elif rhs_kind in ["variable", "constant"] and not expr_info.get(
                    "is_array_element"
                ):
                    rhs_symbol = self.symbol_table.lookup(expr_info.get("name"))
                    if rhs_symbol and rhs_symbol.value is not None:
                        if target_type == "Int" and isinstance(rhs_symbol.value, int):
                            symbol.value = rhs_symbol.value
                            print(
                                f"DEBUG: Updated symbol '{symbol.name}' value from variable '{rhs_symbol.name}' to {symbol.value}"
                            )
                        elif target_type == "Float" and isinstance(
                            rhs_symbol.value, (int, float)
                        ):
                            symbol.value = float(rhs_symbol.value)
                            print(
                                f"DEBUG: Updated symbol '{symbol.name}' value from variable '{rhs_symbol.name}' to {symbol.value}"
                            )
                else:
                    if symbol.value is not None:
                        print(
                            f"DEBUG: Resetting symbol '{symbol.name}' value due to complex assignment."
                        )
                        symbol.value = None

        elif var_info.get("is_array_element"):
            symbol = self.symbol_table.lookup(var_info["name"])
            if symbol and symbol.value is not None:
                print(
                    f"DEBUG: Resetting symbol '{symbol.name}' value due to array element assignment."
                )
                symbol.value = None

        return None

    # --- Binary Op Processing (Simplified - Assumes Left Associativity Handling by Grammar) ---
    # --- Expression Hierarchy ---
    def expression(self, items):
        """
        Process the top-level expression rule.

        This method serves as the entry point for all expression processing
        and just propagates the result from its child nodes.

        Args:
            items: List of child expression components

        Returns:
            Dictionary with expression type information
        """
        print(f"DEBUG: expression received items: {items}")
        result = next((item for item in items if isinstance(item, dict)), None)
        if result:
            return result
        print(f"DEBUG: expression did not find dict result in: {items}")
        meta = get_meta(items)
        if not self.symbol_table.has_errors():
            self.symbol_table.add_error(
                "Internal error processing expression.",
                getattr(meta, "line", "?"),
                getattr(meta, "column", "?"),
            )
        return {"type": "ErrorType", "value": None, "meta": meta}

    def logical_or(self, items: List[Union[    lark.lexer.Token, Dict[str, Optional[Union[str,     lark.lexer.Token]]]]]) -> Dict[str, Optional[Union[str,     lark.lexer.Token]]]:
        """
        Process logical OR expressions: expr OR expr

        Handles the logical OR operator (||), which requires Int operands
        and produces an Int result.

        Args:
            items: List of operands and OR operators

        Returns:
            Dictionary with expression type information
        """
        print(f"DEBUG: logical_or received items: {items}")
        if len(items) == 1:
            result = next((item for item in items if isinstance(item, dict)), None)
            return result or {
                "type": "ErrorType",
                "value": None,
                "meta": get_meta(items),
            }
        elif len(items) > 1:
            return self._process_binary_op(items)
        return {"type": "ErrorType", "value": None, "meta": get_meta(items)}

    def logical_and(self, items: List[Union[Dict[str, Optional[Union[str, bool,     lark.lexer.Token]]],     lark.lexer.Token, Dict[str, Union[int,     lark.lexer.Token, str]], Dict[str, Optional[Union[str,     lark.lexer.Token]]]]]) -> Dict[str, Optional[Union[str,     lark.lexer.Token]]]:
        """
        Process logical AND expressions: expr AND expr

        Handles the logical AND operator (&&), which requires Int operands
        and produces an Int result.

        Args:
            items: List of operands and AND operators

        Returns:
            Dictionary with expression type information
        """
        print(f"DEBUG: logical_and received items: {items}")
        if len(items) == 1:
            result = next((item for item in items if isinstance(item, dict)), None)
            return result or {
                "type": "ErrorType",
                "value": None,
                "meta": get_meta(items),
            }
        elif len(items) > 1:
            return self._process_binary_op(items)
        return {"type": "ErrorType", "value": None, "meta": get_meta(items)}

    def comparison(self, items: List[Any]) -> Dict[str, Optional[Union[str,     lark.lexer.Token]]]:
        """
        Process comparison expressions: expr (>, <, >=, <=, ==, !=) expr

        Handles comparison operators. Operands must have compatible types,
        and the result is always of type Int (used as boolean).

        Args:
            items: List of operands and comparison operator

        Returns:
            Dictionary with expression type information
        """
        print(f"DEBUG: comparison received items: {items}")
        if len(items) == 1:
            result = next((item for item in items if isinstance(item, dict)), None)
            return result or {
                "type": "ErrorType",
                "value": None,
                "meta": get_meta(items),
            }
        elif len(items) > 1:
            return self._process_binary_op(items)
        return {"type": "ErrorType", "value": None, "meta": get_meta(items)}

    def arith_expr(self, items: List[Any]) -> Dict[str, Optional[Union[str,     lark.lexer.Token]]]:
        """
        Process arithmetic expressions: expr (+, -) expr

        Handles addition and subtraction operators.
        Type rules:
        - Int + Int = Int
        - Float + Float = Float
        - Int + Float = Float
        - Float + Int = Float
        Same rules apply for subtraction.

        Args:
            items: List of operands and arithmetic operators

        Returns:
            Dictionary with expression type information
        """
        print(f"DEBUG: arith_expr received items: {items}")
        if len(items) == 1:
            result = next((item for item in items if isinstance(item, dict)), None)
            return result or {
                "type": "ErrorType",
                "value": None,
                "meta": get_meta(items),
            }
        elif len(items) > 1:
            return self._process_binary_op(items)
        return {"type": "ErrorType", "value": None, "meta": get_meta(items)}

    def term(self, items: List[Any]) -> Dict[str, Optional[Union[str,     lark.lexer.Token]]]:
        """
        Process term expressions: expr (*, /) expr

        Handles multiplication and division operators.
        Type rules:
        - Int * Int = Int
        - Float * Float = Float
        - Int * Float = Float
        - Float * Int = Float
        Same rules apply for division.

        Division has special handling for division by zero.

        Args:
            items: List of operands and term operators

        Returns:
            Dictionary with expression type information
        """
        print(f"DEBUG: term received items: {items}")
        if len(items) == 1:
            result = next((item for item in items if isinstance(item, dict)), None)
            return result or {
                "type": "ErrorType",
                "value": None,
                "meta": get_meta(items),
            }
        elif len(items) > 1:
            return self._process_binary_op(items)
        return {"type": "ErrorType", "value": None, "meta": get_meta(items)}

    def _process_binary_op(self, items: List[Any]) -> Dict[str, Optional[Union[str,     lark.lexer.Token]]]:
        """
        Process binary operations with common logic for all binary operators.

        This is a helper method used by all the expression methods that handle
        binary operations. It extracts the operands and operator, checks type
        compatibility, and determines the result type of the operation.

        Supported operators:
        - Arithmetic: +, -, *, /
        - Comparison: >, <, >=, <=, ==, !=
        - Logical: AND, OR

        Args:
            items: List of operands and operator tokens

        Returns:
            Dictionary with expression type information
        """
        print(f"DEBUG: _process_binary_op received items: {items}")
        operands = self._find_all_results(items)
        op_token = None
        operator_types = [
            "PLUS",
            "MINUS",
            "STAR",
            "SLASH",
            "GT",
            "LT",
            "GTE",
            "LTE",
            "EQ",
            "NEQ",
            "AND",
            "OR",
        ]
        for item in items:
            if isinstance(item, Token) and (
                item.type in operator_types or item.value in operator_types
            ):
                op_token = item
                break

        meta = get_meta(
            op_token or (operands[0].get("meta") if operands else None) or items
        )

        if len(operands) == 1 and op_token is None:
            if isinstance(operands[0], dict):
                return operands[0]
            else:
                print(
                    f"DEBUG: _process_binary_op unexpected single operand: {operands[0]}"
                )
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        "Internal error processing single operand expression.",
                        getattr(meta, "line", "?"),
                        getattr(meta, "column", "?"),
                    )
                return {"type": "ErrorType", "value": None, "meta": meta}

        if len(operands) < 2 or op_token is None:
            print(
                f"DEBUG: _process_binary_op failed find operands/operator. Ops: {operands}, Op: {op_token}, Items: {items}"
            )
            if not self.symbol_table.has_errors() and not any(
                isinstance(o, dict) and o.get("type") == "ErrorType" for o in operands
            ):
                self.symbol_table.add_error(
                    "Internal error processing binary operation structure.",
                    getattr(meta, "line", "?"),
                    getattr(meta, "column", "?"),
                )
            return {"type": "ErrorType", "value": None, "meta": meta}

        left = operands[0]
        right = operands[1]
        op_meta = get_meta(op_token)
        op_type = op_token.type

        if not op_meta:
            op_meta = left.get("meta") or right.get("meta") or meta

        left_type = left.get("type")
        right_type = right.get("type")

        if left_type == "ErrorType" or right_type == "ErrorType":
            return {"type": "ErrorType", "value": None, "meta": op_meta}

        if left.get("kind") == "array":
            op_name = left.get("name", "<unknown_array>")
            self.symbol_table.add_error(
                f"Cannot use array '{op_name}' directly in expression with operator '{op_token.value}'. Use array element access (e.g., array[index]).",
                getattr(left.get("meta", op_meta), "line", "?"),
                getattr(left.get("meta", op_meta), "column", "?"),
            )
            return {"type": "ErrorType", "value": None, "meta": op_meta}
        if right.get("kind") == "array":
            op_name = right.get("name", "<unknown_array>")
            self.symbol_table.add_error(
                f"Cannot use array '{op_name}' directly in expression with operator '{op_token.value}'. Use array element access (e.g., array[index]).",
                getattr(right.get("meta", op_meta), "line", "?"),
                getattr(right.get("meta", op_meta), "column", "?"),
            )
            return {"type": "ErrorType", "value": None, "meta": op_meta}

        result_type_str = None

        if op_type == "SLASH":
            if self._check_division_by_zero(right, op_meta):
                return {"type": "ErrorType", "meta": op_meta}
            elif not self._check_type_compatibility(left_type, right_type, op_meta):
                return {"type": "ErrorType", "meta": op_meta}
            else:
                result_type_str = self._result_type(left_type, right_type)
                if result_type_str == "ErrorType":
                    if not self.symbol_table.has_errors():
                        self.symbol_table.add_error(
                            f"Type mismatch during division result calculation ({left_type} / {right_type}).",
                            getattr(op_meta, "line", "?"),
                            getattr(op_meta, "column", "?"),
                        )
                    return {"type": "ErrorType", "meta": op_meta}

        elif op_type in ["PLUS", "MINUS", "STAR"]:
            if not self._check_type_compatibility(left_type, right_type, op_meta):
                return {"type": "ErrorType", "meta": op_meta}
            result_type_str = self._result_type(left_type, right_type)
            if result_type_str == "ErrorType":
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        f"Type mismatch during arithmetic result calculation ({left_type} {op_token.value} {right_type}).",
                        getattr(op_meta, "line", "?"),
                        getattr(op_meta, "column", "?"),
                    )
                return {"type": "ErrorType", "meta": op_meta}

        elif op_type in ["GT", "LT", "GTE", "LTE", "EQ", "NEQ"]:
            if not self._check_type_compatibility(left_type, right_type, op_meta):
                return {"type": "ErrorType", "meta": op_meta}
            result_type_str = "Int"

        elif op_type in ["AND", "OR"]:
            if not (left_type == "Int" and right_type == "Int"):
                self.symbol_table.add_error(
                    f"Logical operator '{op_type}' requires Int operands, got '{left_type}' and '{right_type}'.",
                    getattr(op_meta, "line", "?"),
                    getattr(op_meta, "column", "?"),
                )
                return {"type": "ErrorType", "meta": op_meta}
            result_type_str = "Int"

        else:
            self.symbol_table.add_error(
                f"Internal error: Unhandled binary operator '{op_token.value}' (type {op_type}).",
                getattr(op_meta, "line", "?"),
                getattr(op_meta, "column", "?"),
            )
            return {"type": "ErrorType", "meta": op_meta}

        return {"type": result_type_str, "value": None, "meta": op_meta}

    # --- Control Flow / IO ---
    def conditional(self, items: List[Optional[Union[Dict[str, Optional[Union[str,     lark.lexer.Token]]],     lark.tree.Tree, Dict[str, Union[str, float,     lark.lexer.Token]]]]]) -> None:
        """
        Process an if statement: if (condition) then { instructions } [else { instructions }]

        Validates that the condition expression has type Int (used as boolean).

        Args:
            items: List containing condition expression and statement blocks

        Returns:
            None
        """
        print(f"DEBUG: conditional received items: {items}")
        condition_info = None
        error_found = False

        for item in items:
            if isinstance(item, dict) and item.get("type") == "ErrorType":
                print("DEBUG: conditional found ErrorType propagated from child.")
                error_found = True
                break
        if error_found:
            return None

        found_results = []
        for item in items:
            if isinstance(item, dict) and "type" in item:
                found_results.append(item)
            elif isinstance(item, Tree) and item.data == "comparison":
                print(f"DEBUG: conditional processing comparison tree: {item}")
                left = item.children[0]
                right = item.children[1]

                if not isinstance(left, dict) or not isinstance(right, dict):
                    print("DEBUG: conditional - invalid comparison operands")
                    if not self.symbol_table.has_errors():
                        self.symbol_table.add_error(
                            "Internal error: Invalid comparison operands."
                        )
                    return None

                condition_info = {"type": "Int", "meta": get_meta(item)}
                break

        if not condition_info:
            if len(found_results) == 1:
                condition_info = found_results[0]
                print(f"DEBUG: conditional found condition result: {condition_info}")
            elif len(found_results) > 1:
                print(
                    f"DEBUG: conditional found multiple dict results: {found_results}"
                )
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        "Internal error: Ambiguous structure in if statement."
                    )
                return None
            else:
                print(
                    f"DEBUG: conditional failed find condition result dictionary in items: {items}"
                )
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        "Internal error processing if condition structure."
                    )
                return None

        if condition_info.get("type") != "Int":
            meta = condition_info.get("meta")
            line = getattr(meta, "line", "?")
            col = getattr(meta, "column", "?")
            self.symbol_table.add_error(
                f"Condition for 'if' must be Integer, got '{condition_info.get('type', 'unknown')}'.",
                line,
                col,
            )
            return None

        print("DEBUG: conditional condition type check passed.")
        return None

    def do_while_loop(self, items: List[Optional[Union[Dict[str, Optional[Union[str, bool,     lark.lexer.Token]]],     lark.tree.Tree, Dict[str, Optional[Union[str,     lark.lexer.Token]]]]]]) -> None:
        """
        Process a do-while loop: do { instructions } while (condition)

        Validates that the condition expression has type Int (used as boolean).

        Args:
            items: List containing statement block and condition expression

        Returns:
            None
        """
        print(f"DEBUG: do_while received items: {items}")
        condition_info = None

        condition_item = None
        if items and len(items) > 0:
            for item in reversed(items):
                if isinstance(item, Tree) or isinstance(item, dict):
                    condition_item = item
                    break

        if condition_item is None:
            print(f"DEBUG: do_while failed to find condition item in: {items}")
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error processing while condition structure (missing condition)."
                )
            return None

        if (
            isinstance(condition_item, dict)
            and condition_item.get("type") == "ErrorType"
        ):
            print("DEBUG: do_while found ErrorType propagated from condition.")
            return None

        if isinstance(condition_item, Tree) and condition_item.data == "comparison":
            print(f"DEBUG: do_while processing comparison tree: {condition_item}")
            if len(condition_item.children) >= 2:
                left = condition_item.children[0]
                right = condition_item.children[1]
                if not isinstance(left, dict) or not isinstance(right, dict):
                    print("DEBUG: do_while - invalid comparison operands")
                    if not self.symbol_table.has_errors():
                        self.symbol_table.add_error(
                            "Internal error: Invalid comparison operands in while."
                        )
                    return None
                if not self._check_type_compatibility(
                    left.get("type"), right.get("type"), get_meta(condition_item)
                ):
                    return None
                condition_info = {"type": "Int", "meta": get_meta(condition_item)}
            else:
                print(
                    f"DEBUG: do_while invalid comparison tree structure: {condition_item}"
                )
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        "Internal error processing while comparison structure."
                    )
                return None
        elif isinstance(condition_item, dict) and "type" in condition_item:
            print(f"DEBUG: do_while found direct condition dict: {condition_item}")
            condition_info = condition_item
        else:
            print(f"DEBUG: do_while found unexpected condition item: {condition_item}")
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error processing while condition structure (unexpected item)."
                )
            return None

        if condition_info.get("type") != "Int":
            meta = condition_info.get("meta")
            line = getattr(meta, "line", "?")
            col = getattr(meta, "column", "?")
            self.symbol_table.add_error(
                f"Condition for 'while' must be Integer, got '{condition_info.get('type', 'unknown')}'.",
                line,
                col,
            )
            return None

        print("DEBUG: do_while condition type check passed.")
        return None

    def for_loop(self, items: List[Any]) -> None:
        """
        Process a for loop: for var from expr to expr step expr { instructions }

        Validates:
        - The loop variable must be of type Int
        - The loop variable cannot be a constant
        - The start, end, and step expressions must be of type Int

        Args:
            items: List containing loop variable and start, end, step expressions

        Returns:
            None
        """
        print(f"DEBUG: for_loop received items: {items}")
        loop_var_token = self._find_item(items, "IDENTIFIER")
        expr_results = self._find_all_results(items)
        if not loop_var_token or len(expr_results) < 3:
            print(
                f"DEBUG: for_loop failed find items. var={loop_var_token}, exprs={expr_results}"
            )
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error(
                    "Internal error processing for loop structure."
                )
            return None
        start_expr_info, end_expr_info, step_expr_info = expr_results[0:3]
        symbol = self.symbol_table.lookup(loop_var_token.value, meta=loop_var_token)
        if symbol:
            if symbol.type != "Int":
                self.symbol_table.add_error(
                    f"Loop variable '{loop_var_token.value}' must be Int, got '{symbol.type}'.",
                    loop_var_token.line,
                    loop_var_token.column,
                )
            if symbol.kind == "constant":
                self.symbol_table.add_error(
                    f"Loop variable '{loop_var_token.value}' cannot be a constant.",
                    loop_var_token.line,
                    loop_var_token.column,
                )
        for expr_info, name in [
            (start_expr_info, "start"),
            (end_expr_info, "end"),
            (step_expr_info, "step"),
        ]:
            if not isinstance(expr_info, dict):
                print(f"DEBUG: for_loop invalid expr_info for '{name}': {expr_info}")
                if not self.symbol_table.has_errors():
                    self.symbol_table.add_error(
                        f"Internal error processing '{name}' expression."
                    )
                continue
            if expr_info.get("type") == "ErrorType":
                continue
            if expr_info.get("type") != "Int":
                expr_meta = expr_info.get("meta")
                line = getattr(expr_meta, "line", "?")
                col = getattr(expr_meta, "column", "?")
                self.symbol_table.add_error(
                    f"Expression for '{name}' must be Int, got '{expr_info['type']}'.",
                    line,
                    col,
                )
        return None

    def input_statement(self, items: List[    lark.lexer.Token]) -> None:
        """
        Process an input statement: input(variable)

        Validates that the variable is a valid identifier and not a constant or program name.

        Args:
            items: List containing the identifier to receive input

        Returns:
            None
        """
        print(f"DEBUG: input_statement received items: {items}")
        id_token = self._find_item(items, "IDENTIFIER")
        if not id_token:
            print("DEBUG: input_statement failed find ID token.")
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error("Internal error processing input variable.")
            return None
        symbol = self.symbol_table.lookup(id_token.value, meta=id_token)
        if symbol:
            if symbol.kind == "constant":
                self.symbol_table.add_error(
                    f"Cannot 'input' into constant '{id_token.value}'.",
                    id_token.line,
                    id_token.column,
                )
            elif symbol.kind == "program":
                self.symbol_table.add_error(
                    f"Cannot 'input' into program name '{id_token.value}'.",
                    id_token.line,
                    id_token.column,
                )
        return None

    def output_statement(self, items: List[None]) -> None:
        """
        Process an output statement: output(output_list)

        Args:
            items: List containing the output_list

        Returns:
            None
        """
        return None

    def output_list(self, items: List[Union[Dict[str, Optional[Union[str, bool,     lark.lexer.Token]]],     lark.lexer.Token, Dict[str, Optional[Union[str, bool,     lark.tree.Meta]]], Dict[str, Optional[Union[str, bool, int,     lark.lexer.Token]]]]]) -> None:
        """
        Process an output list: output_item, output_item, ...

        Args:
            items: List of output items

        Returns:
            None
        """
        return None

    def output_item(self, items):
        """
        Process an output item: expression or string

        Validates that the output item is a string or an expression of type Int or Float.
        Array variables must be accessed by element, not as a whole.

        Args:
            items: List containing either a string or an expression

        Returns:
            None
        """
        print(f"DEBUG: output_item received items: {items}")
        item = items[0] if items else None
        if isinstance(item, Token) and item.type == "STRING":
            pass
        elif isinstance(item, dict):
            if item.get("type") == "ErrorType":
                return None
            if item.get("kind") == "array":
                op_name = item.get("name", "<unknown_array>")
                meta = item.get("meta")
                line = getattr(meta, "line", "?")
                col = getattr(meta, "column", "?")
                self.symbol_table.add_error(
                    f"Cannot output entire array '{op_name}'. Output an element (e.g., array[index]) or use a loop.",
                    line,
                    col,
                )
                return None
            if item.get("type") not in ["Int", "Float"]:
                meta = item.get("meta")
                line = getattr(meta, "l", "?")
                col = getattr(meta, "c", "?")
                self.symbol_table.add_error(
                    f"Cannot output type '{item['type']}'. Only Int, Float, or String allowed.",
                    line,
                    col,
                )
        else:
            print(f"DEBUG: output_item invalid item: {item}")
            if not self.symbol_table.has_errors():
                self.symbol_table.add_error("Internal error processing output item.")
        return None

    def empty_instruction(self, items: List[Any]) -> None:
        """
        Process an empty instruction (a bare semicolon).

        Args:
            items: Empty list

        Returns:
            None
        """
        return None

    # --- Helper Methods ---
    def _check_type_compatibility(
        self, type1: str, type2: str, operation_meta: Union[    lark.tree.Meta,     lark.lexer.Token], allow_float_int: bool=True
    ) -> bool:
        """Check if two types are compatible for operations."""
        if not type1 or not type2 or type1 == "ErrorType" or type2 == "ErrorType":
            return False
        if type1 == type2:
            return True
        if allow_float_int and (
            (type1 == "Float" and type2 == "Int")
            or (type1 == "Int" and type2 == "Float")
        ):
            return True
        line = getattr(operation_meta, "line", "?")
        col = getattr(operation_meta, "column", "?")
        self.symbol_table.add_error(
            f"Type mismatch: Cannot operate on '{type1}' and '{type2}'.", line, col
        )
        return False

    def _result_type(self, type1: str, type2: str, allow_float_int: bool=True) -> str:
        """Determine the result type of a binary operation."""
        if not type1 or not type2 or type1 == "ErrorType" or type2 == "ErrorType":
            return "ErrorType"
        if type1 == "Float" or type2 == "Float":
            if allow_float_int and (
                type1 in ["Int", "Float"] and type2 in ["Int", "Float"]
            ):
                return "Float"
        elif type1 == "Int" and type2 == "Int":
            return "Int"
        return "ErrorType"

    def _check_division_by_zero(self, right_operand: Dict[str, Any], meta:     lark.lexer.Token) -> bool:
        """Helper method to check for division by zero."""
        if isinstance(right_operand, dict) and "value" in right_operand:
            op_value = right_operand.get("value")
            right_operand.get("type")

            if op_value == 0:
                line = getattr(meta, "line", "?")
                col = getattr(meta, "column", "?")
                self.symbol_table.add_error("Division by zero.", line, col)
                return True

        return False
