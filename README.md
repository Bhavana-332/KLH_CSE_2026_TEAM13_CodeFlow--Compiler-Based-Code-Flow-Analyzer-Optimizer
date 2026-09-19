# CodeFlow Compiler

**Compiler-Based Code Optimization & Flowchart Visualizer** — a Compiler
Design mini-project. Paste source code in a small educational C-like
language, click **COMPILE & OPTIMIZE**, and watch a real lexer, parser,
semantic analyzer and optimizer run on it — then compare the program's
control-flow graph **before and after optimization**, generated as real
graphical SVG flowcharts (not ASCII art).

```
Source Code → Lexical Analysis → Syntax Analysis → Semantic Analysis
            → Code Optimization → Control Flow Graph → Before/After Compare
```

---

## 1. Architecture

```
frontend (React + Vite)
        |
        |  POST /api/compile  { source: "..." }
        v
backend (FastAPI, Python)
        |
        v
compiler engine (backend/compiler/)
        |
        ├── lexer.py       Lexical Analysis   -> tokens
        ├── parser.py      Syntax Analysis    -> AST
        ├── semantic.py    Semantic Analysis  -> validated AST
        ├── optimizer.py   Code Optimization  -> optimized AST + report
        ├── cfg.py          Control Flow Graph -> positioned graph
        └── svg_render.py   Flowchart render   -> SVG markup
```

The frontend never re-implements any compiler logic — it only displays
whatever JSON the `/api/compile` endpoint returns, so **all Compiler
Design work happens in Python and is fully inspectable**.

## 2. Project structure

```
CodeFlow-Compiler/
├── backend/
│   ├── compiler/
│   │   ├── lexer.py
│   │   ├── parser.py
│   │   ├── ast_nodes.py
│   │   ├── semantic.py
│   │   ├── optimizer.py
│   │   ├── cfg.py
│   │   ├── svg_render.py
│   │   ├── errors.py
│   │   └── compiler.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── samples.js
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 3. The CodeFlow language

A small educational language supporting:

```c
int x = 10;               // declaration
x = x + 5;                // assignment
x + y, x - y, x * y, x / y            // arithmetic
x > 10, x < 20, x == 10, x != 5, x >= 10, x <= 20   // comparisons

if (x > 10) { y = 20; } else { y = 30; }
while (x < 10) { x = x + 1; }
print(x);
```

## 4. Optimizations implemented

| Optimization | Example |
|---|---|
| Constant Folding | `10 + 20` → `30` |
| Algebraic Simplification | `x + 0` → `x`, `x * 1` → `x`, `x * 0` → `0` |
| Constant Condition | `if (1) { A } else { B }` → `A` (branch inlined, diamond removed) |
| Dead Code Elimination | An assignment overwritten before it's ever read is removed |

## 5. Compiler Design concept map (for viva)

| Compiler Concept | Project Component |
|---|---|
| Lexical Analysis | `backend/compiler/lexer.py` |
| Syntax Analysis | `backend/compiler/parser.py` |
| Semantic Analysis | `backend/compiler/semantic.py` |
| Intermediate Representation | `backend/compiler/ast_nodes.py` (the AST) |
| Code Optimization | `backend/compiler/optimizer.py` |
| Control Flow Graph | `backend/compiler/cfg.py` + `svg_render.py` |

**Data flow:** the raw source string is tokenized by the `Lexer`, the
token stream is turned into an `AST` by the `Parser`, the `AST` is
validated in place by the `SemanticAnalyzer`, a **new** optimized AST is
produced by the `Optimizer` (which also records every transformation it
makes), and finally `cfg.py` walks **both** the original and the
optimized AST independently to build two control-flow graphs, which
`svg_render.py` turns into the two SVG flowcharts you see side by side.
Nothing is hard-coded per sample — every part of the pipeline works on
whatever program you type in.

---

## 6. Windows setup (from zero)

### Software to install

1. **Python 3.10+** — https://www.python.org/downloads/ (check "Add
   python.exe to PATH" during install)
2. **Node.js 18+ (LTS)** — https://nodejs.org/

Verify both installed correctly:

```powershell
python --version
node --version
npm --version
```

### Unzip the project

Unzip `CodeFlow-Compiler.zip` anywhere, e.g. `C:\Projects\CodeFlow-Compiler`,
then open **two** PowerShell / Command Prompt windows (one for backend,
one for frontend).

### Backend setup (Terminal 1)

```powershell
cd CodeFlow-Compiler\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend setup (Terminal 2)

```powershell
cd CodeFlow-Compiler\frontend
npm install
```

---

## 7. Running the project

### Terminal 1 — start the backend

```powershell
cd CodeFlow-Compiler\backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

You should see `Uvicorn running on http://127.0.0.1:8000`. Leave this
window open.

### Terminal 2 — start the frontend

```powershell
cd CodeFlow-Compiler\frontend
npm run dev
```

You should see `Local: http://localhost:5173/`. Leave this window open
too.

### Open the app

Open **http://localhost:5173** in your browser. A sample program is
pre-loaded — click **⚡ COMPILE & OPTIMIZE**.

(If macOS/Linux instead of Windows: same commands, but use
`source venv/bin/activate` instead of `venv\Scripts\activate`.)

---

## 8. Testing the project

Use the **sample dropdown** in the editor toolbar to load these, or
paste them yourself:

1. **Constant folding** — `int x = 10 + 20; int y = x * 1; print(y);`
   → optimized code becomes `int x = 30; int y = x;`

2. **Constant branch (biggest visual difference)** — an `if (1) {...}
   else {...}` — the *Before* flowchart shows a diamond with two
   branches; the *After* flowchart has **no diamond at all**, just a
   straight line, because the optimizer proved the condition is always
   true and removed the branch entirely.

3. **While loop** — shows a decision diamond with a dashed
   **loop back** edge curving back into it — demonstrates a real
   back-edge in the control flow graph.

4. **Invalid code**, e.g. `int x = ;` — the app shows a clean red
   error panel with the stage, message, line number and offending
   source line instead of crashing.

5. **Semantic errors**, e.g. `x = 10;` (never declared), or
   `int x = 10; int x = 20;` (duplicate declaration) — both produce
   clear semantic error panels.

Check each of the five tabs after a successful compile: **Token
Explorer**, **AST Viewer**, **Optimization Report**, **Before/After
Flowcharts**, **Code Comparison** — plus the **Statistics** cards
above them.

---

## 9. Troubleshooting

- **Frontend shows "Could not reach the CodeFlow backend"** — make sure
  the `uvicorn` terminal is still running and didn't error out; it must
  be on port 8000.
- **`pip install` fails** — make sure the virtual environment is
  activated (you should see `(venv)` in your prompt) and you're using
  Python 3.10+.
- **Port already in use** — stop whatever else is using port 8000 or
  5173, or run `uvicorn main:app --reload --port 8001` and set
  `VITE_API_BASE=http://localhost:8001` in a `.env` file inside
  `frontend/`.
