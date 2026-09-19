"""
CodeFlow Compiler - FastAPI backend entry point.

Exposes a single POST /api/compile endpoint that runs the full
compiler pipeline (lexer -> parser -> semantic analyzer -> optimizer ->
CFG -> SVG) on the submitted source code and returns a structured
JSON result for the React frontend to render.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from compiler.compiler import compile_source

app = FastAPI(title="CodeFlow Compiler API", version="1.0.0")

# Allow the Vite dev server (and a same-origin build) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://codeflow-compiler.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompileRequest(BaseModel):
    source: str


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CodeFlow Compiler API"}


@app.post("/api/compile")
def compile_endpoint(payload: CompileRequest):
    result = compile_source(payload.source)
    return result
