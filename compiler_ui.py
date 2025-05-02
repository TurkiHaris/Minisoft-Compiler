import streamlit as st
from lark import Lark, exceptions, Tree, Token  # Import Tree and Token
from src.semantic_analyzer import (
    SemanticAnalyzer,
    get_meta,
    SymbolTable,
)  # Assuming SymbolTable is needed for type hinting/instance checks
import pandas as pd
import traceback

# --- Grammar Loading ---
try:
    with open("src/minisoft.lark", "r") as f:
        GRAMMAR = f.read()
    PARSER = Lark(GRAMMAR, start="program", parser="lalr", propagate_positions=True)
except FileNotFoundError:
    st.error(
        "Fatal Error: Grammar file 'minisoft.lark' not found in the current directory."
    )
    st.stop()
except Exception as e:
    st.error(f"Fatal Error loading grammar: {e}")
    st.stop()


# --- Function to Convert Lark Tree to Dict ---
def lark_tree_to_dict(node):
    if isinstance(node, Tree):
        return {node.data: [lark_tree_to_dict(child) for child in node.children]}
    elif isinstance(node, Token):
        return {"TOKEN": node.type, "value": node.value}
    else:
        return str(node)


# --- Function to Render Tree with Box-Drawing Characters ---
def render_tree_text(node, prefix="", is_last=True):
    """Recursively builds a list of strings representing the tree with box-drawing characters."""
    lines = []
    connector = "└─ " if is_last else "├─ "
    if isinstance(node, Tree):
        lines.append(f"{prefix}{connector}**{node.data}** (Rule)")
        child_prefix = prefix + ("   " if is_last else "│  ")
        children = node.children
        for i, child in enumerate(children):
            is_last_child = i == len(children) - 1
            lines.extend(render_tree_text(child, child_prefix, is_last_child))
    elif isinstance(node, Token):
        value_escaped = str(node.value).replace("`", "\\`")
        lines.append(f"{prefix}{connector}`{node.type}`: `{value_escaped}` (Token)")
    else:
        lines.append(f"{prefix}{connector}{str(node)}")

    return lines


# --- Core Compilation Logic ---
def compile_source(source_code: str):
    results = {
        "parsing_log": [],
        "parsing_error": None,
        "parse_tree_obj": None,  # Re-added
        "parse_tree_dict": None,
        "semantic_log": [],
        "semantic_errors": None,
        "symbol_table_df": None,
        "success": False,
    }
    parse_tree = None

    # --- 1. Parsing Lexical and Syntax Analysis ---
    results["parsing_log"].append("Starting parsing...")
    try:
        parse_tree = PARSER.parse(source_code)
        results["parse_tree_obj"] = parse_tree
        results["parse_tree_dict"] = lark_tree_to_dict(parse_tree)
        results["parsing_log"].append("Parsing successful.")
    # Catch Lexical Errors
    except exceptions.UnexpectedCharacters as e:
        error_msg = f"Lexical Error: Unexpected characters at line {e.line}, column {e.column}.\n"
        try:
            # Attempt to show the problematic character sequence
            context_line = source_code.splitlines()[e.line - 1]
            # Highlight the specific character if possible, otherwise the general area
            error_char_index = (
                e.pos_in_stream - source_code.find(context_line)
                if context_line in source_code
                else e.column - 1
            )
            if 0 <= error_char_index < len(context_line):
                error_msg += f"Context: {context_line}\n"
                error_msg += " " * (len("Context: ") + error_char_index) + "^"
            else:  # Fallback if index calculation is off
                error_msg += f"Context: {context_line}\n"
                error_msg += " " * (len("Context: ") + e.column - 1) + "^"

        except IndexError:
            error_msg += f"(Could not retrieve context line {e.line})"
        except Exception as context_err:
            error_msg += f"(Error retrieving context: {context_err})"

        results["parsing_error"] = error_msg
        results["parsing_log"].append("Parsing failed (Lexical Error).")
        return results  # Stop compilation here
    # Catch Syntax Errors
    except exceptions.UnexpectedToken as e:
        error_msg = f"Syntax Error: Unexpected token '{e.token}' at line {e.line}, column {e.column}.\n"
        error_msg += f"Expected one of: {e.expected}\n"
        try:
            context = source_code.splitlines()[e.line - 1]
            error_msg += f"Context: {context}\n"
            error_msg += " " * (len("Context: ") + e.column - 1) + "^"
        except IndexError:
            error_msg += "(Could not retrieve context line)"
        results["parsing_error"] = error_msg
        results["parsing_log"].append("Parsing failed (Syntax Error).")
        return results  # Stop compilation here

    # Catch other general parsing errors
    except exceptions.LarkError as e:
        results["parsing_error"] = f"Parsing Error: {e}"
        results["parsing_log"].append("Parsing failed.")
        return results  # Stop compilation here

    # Catch other potential parsing errors
    except Exception as e:
        results["parsing_error"] = (
            f"Unexpected Parsing Error: {e}\n{traceback.format_exc()}"
        )
        results["parsing_log"].append("Parsing failed unexpectedly.")
        return results

    # --- 2. Semantic Analysis ---
    results["semantic_log"].append("Starting semantic analysis...")
    analyzer = SemanticAnalyzer()
    symbol_table_result = None
    try:
        if parse_tree:
            symbol_table_result = analyzer.transform(parse_tree)
        else:
            raise ValueError("Parse tree object is missing for semantic analysis.")

        if isinstance(symbol_table_result, SymbolTable):
            if symbol_table_result.has_errors():
                results["semantic_errors"] = symbol_table_result.get_errors()
                results["semantic_log"].append(
                    "Semantic analysis completed with errors."
                )
            else:
                results["semantic_log"].append(
                    "Semantic analysis successful. No errors detected."
                )
                st_data = []
                headers = ["Name", "Kind", "Type", "Value", "Size", "Declared At"]
                for name, symbol in symbol_table_result._symbols.items():
                    kind_str = str(symbol.kind) if symbol.kind is not None else "N/A"
                    type_str = str(symbol.type) if symbol.type is not None else "N/A"
                    value_str = str(symbol.value) if symbol.value is not None else "N/A"
                    size_str = str(symbol.size) if symbol.size is not None else "N/A"
                    loc_str = (
                        f"line {symbol.declared_at[0]}, col {symbol.declared_at[1]}"
                        if symbol.declared_at
                        else "N/A"
                    )
                    st_data.append(
                        [name, kind_str, type_str, value_str, size_str, loc_str]
                    )

                if st_data:
                    results["symbol_table_df"] = pd.DataFrame(st_data, columns=headers)
                else:
                    results["semantic_log"].append("Symbol table is empty.")
                results["success"] = True
        else:
            results["semantic_errors"] = [
                "Semantic analysis did not return a valid SymbolTable object."
            ]
            results["semantic_log"].append("Semantic analysis failed internally.")

    except exceptions.VisitError as e:
        error_msg = f"Error during Semantic Analysis: {e.orig_exc.__class__.__name__}: {e.orig_exc}\n"
        meta = get_meta(e.obj)
        if meta:
            error_msg += (
                f"Approximate location: line {meta.line}, column {meta.column}\n"
            )
        else:
            error_msg += f"Error occurred processing node: {e.obj}\n"
        error_msg += "\n--- Traceback for Original Error ---\n"
        error_msg += "".join(
            traceback.format_exception(
                type(e.orig_exc), e.orig_exc, e.orig_exc.__traceback__
            )
        )
        error_msg += "------------------------------------"
        results["semantic_errors"] = [error_msg]
        results["semantic_log"].append("Semantic analysis failed.")

    except Exception as e:
        error_msg = f"Unexpected Semantic Analysis Error: {e}\n{traceback.format_exc()}"
        results["semantic_errors"] = [error_msg]
        results["semantic_log"].append("Semantic analysis failed unexpectedly.")

    return results


# --- Streamlit UI ---
def main():
    st.set_page_config(layout="wide")
    st.title("MiniSoft Compiler Interface")
    st.subheader("Authors: TURKI HARIS & ZITOUNI OUSSAMA")

    # Initialize session state if not already done
    if "compile_results" not in st.session_state:
        st.session_state.compile_results = None
    if "uploaded_code" not in st.session_state:
        st.session_state.uploaded_code = None

    # --- Section 1: Upload and Compile ---
    st.header("1. Upload Source File")
    # Key is important for Streamlit to detect changes properly
    uploaded_file = st.file_uploader(
        "Choose a MiniSoft file (.ms)", type=["ms", "txt"], key="file_uploader"
    )

    # Process uploaded file immediately
    code_changed = False
    newly_uploaded_code = None

    if uploaded_file is not None:
        try:
            # Read the file content efficiently
            newly_uploaded_code = uploaded_file.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            newly_uploaded_code = None  # Ensure it's None on error

    # Check if the code content has changed or file removed
    if newly_uploaded_code is not None:
        # Check if the content is actually different from what's stored
        if st.session_state.uploaded_code != newly_uploaded_code:
            st.session_state.uploaded_code = newly_uploaded_code
            st.session_state.compile_results = None  # Clear old results on new code
            code_changed = True
    elif (
        st.session_state.uploaded_code is not None
    ):  # File was present, now it's None (cleared)
        st.session_state.uploaded_code = None
        st.session_state.compile_results = None
        code_changed = True

    # Display uploaded code if available in session state
    if st.session_state.uploaded_code:
        with st.expander(
            "View Uploaded Code", expanded=True
        ):  # Expand by default when code is present
            st.code(st.session_state.uploaded_code, language=None)

    # Compile button
    compile_button = st.button("Compile")

    if compile_button:
        if st.session_state.uploaded_code:
            with st.spinner("Compiling..."):
                st.session_state.compile_results = compile_source(
                    st.session_state.uploaded_code
                )
            code_changed = True  # Mark change to trigger rerun after compilation
        else:
            st.warning("Please upload a file first.")
            # State is already cleared if file was removed, no action needed here

    # Rerun the script if the code changed (upload/removal/compile) to update UI
    if code_changed:
        st.rerun()

    # --- Section 2: Parsing Output ---
    st.header("2. Parsing (Lexical & Syntax Analysis)")
    show_tree = st.checkbox("Show Parse Tree", key="show_parse_tree")

    if st.session_state.compile_results:
        results = st.session_state.compile_results
        st.text("Parsing Log:")
        st.code("\n".join(results["parsing_log"]), language=None)

        # Conditionally display parse tree using text rendering
        if show_tree and results.get("parse_tree_obj"):
            st.text("Parse Tree (Text View):")
            tree_lines = render_tree_text(
                results["parse_tree_obj"], prefix="", is_last=True
            )
            if tree_lines:
                st.code("\n".join(tree_lines), language="text")
            st.markdown("---")

        if results["parsing_error"]:
            st.error(f"**Parsing Failed:**\n```\n{results['parsing_error']}\n```")
    else:
        # Show this message only if code has been uploaded but not compiled yet, or if compile failed
        if st.session_state.uploaded_code:
            st.info("Click 'Compile' to see parsing results.")
        else:
            st.info("Upload a file to begin.")  # Changed initial message

    # --- Section 3: Semantic Analysis Output ---
    st.header("3. Semantic Analysis")
    if (
        st.session_state.compile_results
        and st.session_state.compile_results["parsing_error"] is None
    ):
        results = st.session_state.compile_results
        st.code("\n".join(results["semantic_log"]), language=None)
        if results["semantic_errors"]:
            st.error("**Semantic Analysis Failed:**")
            for error in results["semantic_errors"]:
                st.code(error, language=None)

    elif (
        st.session_state.compile_results
        and st.session_state.compile_results["parsing_error"] is not None
    ):
        st.warning("Semantic analysis skipped due to parsing errors.")
    else:
        # Show message based on whether code is ready for compilation
        if st.session_state.uploaded_code:
            st.info("Parsing must succeed before semantic analysis can run.")
        else:
            st.info("Upload a file and click 'Compile'.")

    # --- Section 4: Symbol Table ---
    st.header("4. Symbol Table")
    if st.session_state.compile_results and st.session_state.compile_results["success"]:
        results = st.session_state.compile_results
        if results["symbol_table_df"] is not None and not results["symbol_table_df"].empty:
            st.dataframe(results["symbol_table_df"], use_container_width=True)
        elif results["symbol_table_df"] is not None and results["symbol_table_df"].empty:
            st.info("Symbol table generated successfully, but it is empty.")
        else:
            st.info("No symbol table data available.")
    elif (
        st.session_state.compile_results and not st.session_state.compile_results["success"]
    ):
        st.warning("Symbol table cannot be shown due to compilation errors.")
    else:
        # Show message based on whether code is ready for compilation
        if st.session_state.uploaded_code:
            st.info("Successful compilation is required to display the symbol table.")
        else:
            st.info("Upload a file and click 'Compile'.")

    # --- Footer/Instructions ---
    st.markdown("---")
    st.caption("Upload a `.ms` file, click Compile, and view the results above.")


if __name__ == "__main__":
    main()
