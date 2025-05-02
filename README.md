# MiniSoft Compiler

A teaching compiler for the MiniSoft language, implemented in Python 3.11+. It performs lexical/syntax analysis with Lark and semantic analysis with a custom Transformer. Offers both a command‑line interface and an interactive Streamlit web UI.

> 📚 📚 This application was developed as part of a university project for the course Compiler Design 1, showcasing the practical application of compiler construction techniques using Python.

## 🚀 Features

- Full LALR grammar for MiniSoft language implementation
- Comprehensive semantic analysis with static type checking
- Rich error reporting for lexical, syntax, and semantic errors
- Language features supported:
  - Variable declarations (Int, Float, arrays)
  - Constant declarations with compile-time value checking
  - Identifier validation (max length 14, no trailing/consecutive underscores)
  - Array bounds checking and division-by-zero detection
  - Control flow (if/else, do-while, for-loops)
  - Input/output operations
  - Expression evaluation with operator precedence
  - Constant folding and value tracking
- Command-line interface with detailed compilation reports
- Interactive Streamlit web UI with:
  - Visual parse tree explorer
  - Formatted symbol table view using Pandas
  - Syntax highlighting and error visualization

## 🛠️ Requirements

- Python 3.11 or newer (specified in `.python-version`)
- Dependencies:
  - [Lark](https://github.com/lark-parser/lark) ≥ 1.2.2 (parser generator)
  - [Streamlit](https://streamlit.io) ≥ 1.44.1 (web UI)
  - [Pandas](https://pandas.pydata.org/) >=2.2.3 (table display in web UI)

## 📦 Installation

### Using UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/TurkiHaris/Minisoft-Compiler

cd Minisoft-Compiler

# Create virtual environment and install dependencies with UV
pip install uv
uv sync

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/macOS:
# source .venv/bin/activate
```

### Alternative Installation Methods

```bash
# Using pip
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -e .

# Using Poetry
poetry install
```

## 💻 Usage

### Command-Line Interface

Run the compiler on a MiniSoft (.ms) source file:

```bash
python compiler.py tests/test_valid.ms
python compiler.py tests/test_invalid.ms
```

The CLI will:
- Parse the input file
- Perform semantic analysis
- Report any errors found
- Display the symbol table on successful compilation

### Web Interface

Start the Streamlit web interface:

```bash
streamlit run compiler_ui.py
```

This opens a browser window where you can:
- Upload a .ms file
- View the parse tree visualization
- See detailed semantic errors (if any)
- Explore the symbol table in a DataFrame

## 📁 Project Structure

```
Minisoft-Compiler/
├─ compiler.py        # Command-line compiler driver
├─ compiler_ui.py     # Streamlit web interface
├─ pyproject.toml     # Project metadata and dependencies
├─ uv.lock            # UV dependency lock file
├─ .python-version    # Python version specification
│
├─ src/               # Core compiler components
│  ├─ parser.py       # Wrapper for Lark parser
│  ├─ minisoft.lark   # Grammar definition in Lark format
│  ├─ semantic_analyzer.py # AST transformer with type checking
│  └─ symbol_table.py # Symbol management and error reporting
│
└─ tests/             # Test files
   ├─ test_valid.ms   # Correct MiniSoft program for testing
   └─ test_invalid.ms # Test file with intentional errors
```

## ⚡ Sample MiniSoft Program

```
MainPrgm Example;

Var
  let counter : Int;
  let average : Float;
  let data : [Int; 10];
  @define Const MAX_SIZE : Int = 100;

BeginPg
{
  counter := 0;
  average := 0.0;
  
  output("Enter a value: ");
  input(counter);
  
  if (counter > 0) then {
    data[0] := counter;
    output("Value stored in array.");
  }
}
EndPg;
```

## 🧪 Testing

The project includes test files in the `tests/` directory:

- `test_valid.ms`: A comprehensive valid program that demonstrates all language features
- `test_invalid.ms`: Contains intentional errors to test the error detection capabilities

Run the tests with:

```bash
python compiler.py tests/test_valid.ms
python compiler.py tests/test_invalid.ms
```

## 📄 License

This project is provided solely for educational purposes.  
You may use, copy, and modify the code for non-commercial, educational use only.
