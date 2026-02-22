from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import json
import pickle

import faiss
import networkx as nx
from sentence_transformers import SentenceTransformer


@dataclass
class Chunk:
    id: str
    text: str
    source: str  # filepath


class GraphRAGStore:
    def __init__(
        self,
        index_path: str = "graphrag/faiss.index",
        meta_path: str = "graphrag/meta.json",
        graph_path: str = "graphrag/graph.gpickle",
    ):
        self.index_path = Path(index_path)
        self.meta_path = Path(meta_path)
        self.graph_path = Path(graph_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.meta: List[dict] = []
        self.g = nx.Graph()

        if self.index_path.exists() and self.meta_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            self.meta = json.loads(self.meta_path.read_text(encoding="utf-8"))

        if self.graph_path.exists():
            try:
                with open(self.graph_path, "rb") as f:
                    self.g = pickle.load(f)
            except Exception:
                # Fallback: recréer un graphe vide si fichier corrompu/incompatible
                self.g = nx.Graph()

    def _embed(self, texts: List[str]):
        emb = self.model.encode(texts, normalize_embeddings=True)
        return emb.astype("float32")

    def save(self):
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))

        self.meta_path.write_text(
            json.dumps(self.meta, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        with open(self.graph_path, "wb") as f:
            pickle.dump(self.g, f, protocol=pickle.HIGHEST_PROTOCOL)

    def build_vectors(self, chunks: List[Chunk]):
        if not chunks:
            self.index = None
            self.meta = []
            return

        vecs = self._embed([c.text for c in chunks])
        dim = vecs.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # cosine similarity (normalize + inner product)
        self.index.add(vecs)

        self.meta = [{"id": c.id, "text": c.text, "source": c.source} for c in chunks]

    def vector_search(self, query: str, k: int = 5) -> List[Tuple[dict, float]]:
        if self.index is None:
            return []

        qv = self._embed([query])
        scores, ids = self.index.search(qv, k)

        out: List[Tuple[dict, float]] = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:
                continue
            out.append((self.meta[idx], float(score)))
        return out