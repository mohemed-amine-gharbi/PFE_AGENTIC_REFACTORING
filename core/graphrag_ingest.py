from __future__ import annotations
from pathlib import Path
from typing import List, Set
import ast
import re
import hashlib

from .graphrag_store import GraphRAGStore, Chunk


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + max_chars])
        i += max_chars - overlap
    return chunks


def stable_id(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()[:16]


def extract_symbols_python(code: str) -> Set[str]:
    """Classes, fonctions, imports via AST."""
    symbols: Set[str] = set()
    try:
        tree = ast.parse(code)
    except Exception:
        return symbols

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            symbols.add(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                symbols.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                symbols.add(node.module.split(".")[0])
            for alias in node.names:
                symbols.add(alias.name)
    return symbols


def extract_mentions_symbols(text: str) -> Set[str]:
    """Heuristique: CamelCase + identifiants snake_case."""
    camel = set(re.findall(r"\b[A-Z][a-zA-Z0-9_]{2,}\b", text))
    snake = set(re.findall(r"\b[a-z_][a-z0-9_]{2,}\b", text))
    bad = {"return", "import", "from", "class", "def", "self", "True", "False", "None"}
    return {t for t in (camel | snake) if t not in bad and 2 < len(t) <= 60}


def ingest(paths: List[str], patterns=("**/*.py", "**/*.md", "**/*.txt")):
    store = GraphRAGStore()
    all_chunks: List[Chunk] = []

    for base in paths:
        base_path = Path(base)
        if not base_path.exists():
            continue

        for pat in patterns:
            for file in base_path.glob(pat):
                try:
                    text = file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                file_node = f"file:{file.as_posix()}"
                store.g.add_node(file_node, type="file", path=file.as_posix())

                # Symbols defined/imported in this file
                symbols = set()
                if file.suffix == ".py":
                    symbols |= extract_symbols_python(text)

                for sym in symbols:
                    sym_node = f"symbol:{sym}"
                    store.g.add_node(sym_node, type="symbol", name=sym)
                    store.g.add_edge(sym_node, file_node, rel="defined_in")

                # Chunk nodes + mention edges
                for part in chunk_text(text):
                    cid = stable_id(file.as_posix() + ":" + part[:250])
                    chunk_node = f"chunk:{cid}"
                    all_chunks.append(Chunk(id=cid, text=part, source=file.as_posix()))

                    store.g.add_node(chunk_node, type="chunk", id=cid, source=file.as_posix())
                    store.g.add_edge(chunk_node, file_node, rel="in_file")

                    # Mentions -> symbols
                    mentions = extract_mentions_symbols(part)
                    for m in mentions:
                        m_node = f"symbol:{m}"
                        store.g.add_node(m_node, type="symbol", name=m)
                        store.g.add_edge(chunk_node, m_node, rel="mentions")

    store.build_vectors(all_chunks)
    store.save()
    print(f"✅ GraphRAG indexed {len(all_chunks)} chunks. Saved to graphrag/")

if __name__ == "__main__":
    ingest(["knowledge", "core", "agents"])
