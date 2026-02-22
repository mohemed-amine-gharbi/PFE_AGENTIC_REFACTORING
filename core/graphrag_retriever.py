from __future__ import annotations
from typing import List, Dict, Any, Set
import networkx as nx

from .graphrag_store import GraphRAGStore


class GraphRAGRetriever:
    def __init__(self):
        self.store = GraphRAGStore()

    def _extract_symbols_from_text(self, text: str) -> Set[str]:
        # utilise les nodes existants du graphe: on prend les symboles connus qui apparaissent dans la query
        # MVP: match simple par inclusion (ok sur repo)
        symbols = set()
        for n, data in self.store.g.nodes(data=True):
            if data.get("type") == "symbol":
                name = data.get("name")
                if name and name in text:
                    symbols.add(name)
        return symbols

    def _neighbors_hops(self, start_nodes: List[str], hops: int = 2) -> Set[str]:
        visited = set(start_nodes)
        frontier = set(start_nodes)
        for _ in range(hops):
            nxt = set()
            for node in frontier:
                nxt |= set(self.store.g.neighbors(node))
            nxt -= visited
            visited |= nxt
            frontier = nxt
        return visited

    def retrieve(self, query: str, k_seeds: int = 4, hops: int = 2, max_chunks: int = 8) -> Dict[str, Any]:
        # 1) vector seeds
        seeds = self.store.vector_search(query, k=k_seeds)

        seed_chunk_ids = [m["id"] for (m, _) in seeds]
        seed_chunk_nodes = [f"chunk:{cid}" for cid in seed_chunk_ids if f"chunk:{cid}" in self.store.g]

        # 2) symbols from query + seeds
        seed_text = "\n".join([m["text"] for (m, _) in seeds])
        symbols = self._extract_symbols_from_text(query + "\n" + seed_text)

        symbol_nodes = [f"symbol:{s}" for s in symbols if f"symbol:{s}" in self.store.g]

        # 3) expand graph
        start = seed_chunk_nodes + symbol_nodes
        expanded_nodes = self._neighbors_hops(start, hops=hops)

        # 4) collect chunks from expanded neighborhood
        chunk_nodes = [n for n in expanded_nodes if n.startswith("chunk:")]
        # prioritize: seeds first
        ordered_chunk_nodes = seed_chunk_nodes + [c for c in chunk_nodes if c not in seed_chunk_nodes]
        ordered_chunk_nodes = ordered_chunk_nodes[:max_chunks]

        # build context pack
        chunks_out = []
        for cn in ordered_chunk_nodes:
            cid = cn.split("chunk:")[1]
            meta_item = next((x for x in self.store.meta if x["id"] == cid), None)
            if meta_item:
                chunks_out.append(meta_item)

        # graph facts (light)
        facts = []
        for s in list(symbols)[:12]:
            sn = f"symbol:{s}"
            if sn in self.store.g:
                neigh = list(self.store.g.neighbors(sn))[:8]
                facts.append({"symbol": s, "neighbors": neigh})

        return {
            "seeds": [{"source": m["source"], "score": sc} for (m, sc) in seeds],
            "symbols": sorted(list(symbols))[:50],
            "chunks": chunks_out,
            "facts": facts,
        }

    @staticmethod
    def format_context(pack: Dict[str, Any]) -> str:
        parts = []
        parts.append("### GraphRAG Context")
        if pack.get("symbols"):
            parts.append("**Symbols:** " + ", ".join(pack["symbols"][:20]))
        parts.append("\n### Retrieved Chunks")
        for c in pack.get("chunks", []):
            parts.append(f"\n[SOURCE: {c['source']}]\n{c['text']}")
        return "\n".join(parts)
