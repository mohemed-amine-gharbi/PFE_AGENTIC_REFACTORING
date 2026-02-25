from __future__ import annotations
from typing import List, Dict, Any, Set, Tuple
from pathlib import Path
import re
import networkx as nx

from .graphrag_store import GraphRAGStore


class GraphRAGRetriever:
    """
    Retriever GraphRAG avec filtrage des sources + priorité au dossier knowledge/.
    Objectif:
    - privilégier knowledge/{language}/ + knowledge/shared/
    - éviter la pollution par agents/, workflow, __pycache__, etc.
    """

    # Dossiers/artefacts à exclure
    EXCLUDED_DIR_TOKENS = {
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "test_results",
        "graphrag",  # évite de récupérer les fichiers d'index/meta eux-mêmes
    }

    # Fichiers internes à exclure (polluent souvent le contexte)
    EXCLUDED_FILE_NAMES = {
        "base_agent.py",
        "merge_agent.py",
        "langgraph_orchestrator.py",
        "workflow_graph.py",
        "workflow_nodes.py",
        "workflow_state.py",
    }

    # Sous-chaînes de chemins à exclure
    EXCLUDED_PATH_SUBSTRINGS = {
        "agents/",
        "core/langgraph_orchestrator.py",
        "core/workflow_graph.py",
        "core/workflow_nodes.py",
        "core/workflow_state.py",
    }

    # Extensions non utiles en RAG
    EXCLUDED_EXTENSIONS = {
        ".pyc", ".xlsx", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".log"
    }

    def __init__(self):
        self.store = GraphRAGStore()

    # ----------------------- Utils de filtrage / priorité -----------------------

    def _normalize_path(self, p: str) -> str:
        return str(p).replace("\\", "/").strip().lower()

    def _infer_language_from_query(self, query: str) -> str | None:
        q = query.lower()
        # mapping simple
        langs = [
            "python", "javascript", "typescript", "java", "cpp", "c++", "csharp", "c#",
            "go", "ruby", "rust", "php"
        ]
        for lang in langs:
            if lang in q:
                if lang == "c++":
                    return "cpp"
                if lang == "c#":
                    return "csharp"
                return lang
        return None

    def _is_allowed_source(self, source: str) -> bool:
        if not source:
            return False

        src = self._normalize_path(source)
        p = Path(src)

        if p.suffix.lower() in self.EXCLUDED_EXTENSIONS:
            return False

        if p.name.lower() in self.EXCLUDED_FILE_NAMES:
            return False

        parts = set(p.parts)
        if any(tok in parts for tok in self.EXCLUDED_DIR_TOKENS):
            return False

        if any(token in src for token in self.EXCLUDED_PATH_SUBSTRINGS):
            return False

        return True

    def _source_priority(self, source: str, query: str) -> int:
        """
        Score de priorité (plus petit = meilleur)
        0 = knowledge/{language}/...
        1 = knowledge/shared/...
        2 = autre source autorisée
        9 = source rejetée
        """
        if not self._is_allowed_source(source):
            return 9

        src = self._normalize_path(source)
        lang = self._infer_language_from_query(query)

        # priorité forte : knowledge/langage
        if lang and f"knowledge/{lang}/" in src:
            return 0

        # fallback utile : knowledge/shared
        if "knowledge/shared/" in src:
            return 1

        # autres sources autorisées (si tu veux les garder)
        return 2

    def _prioritize_items(self, items: List[dict], query: str, max_items: int) -> List[dict]:
        unique: List[dict] = []
        seen_ids = set()

        for m in items:
            mid = m.get("id")
            if mid in seen_ids:
                continue
            if not self._is_allowed_source(m.get("source", "")):
                continue
            unique.append(m)
            seen_ids.add(mid)

        unique.sort(key=lambda m: (self._source_priority(m.get("source", ""), query), m.get("source", "")))
        return unique[:max_items]

    # ----------------------- Logique RAG existante -----------------------

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
                try:
                    nxt |= set(self.store.g.neighbors(node))
                except Exception:
                    # sécurité si node absent/invalide
                    continue
            nxt -= visited
            visited |= nxt
            frontier = nxt
        return visited

    def retrieve(self, query: str, k_seeds: int = 4, hops: int = 2, max_chunks: int = 8) -> Dict[str, Any]:
        # 1) vector seeds (sur-échantillonnage puis filtrage)
        raw_k = max(k_seeds * 4, 12)
        raw_seeds: List[Tuple[dict, float]] = self.store.vector_search(query, k=raw_k)

        # filtrer + prioriser les seeds
        filtered_seed_items = []
        score_by_id = {}
        for m, sc in raw_seeds:
            if self._is_allowed_source(m.get("source", "")):
                filtered_seed_items.append(m)
                score_by_id[m["id"]] = float(sc)

        filtered_seed_items = self._prioritize_items(filtered_seed_items, query, max_items=k_seeds)

        # reconstruire seeds avec score
        seeds: List[Tuple[dict, float]] = [(m, score_by_id.get(m["id"], 0.0)) for m in filtered_seed_items]

        seed_chunk_ids = [m["id"] for (m, _) in seeds]
        seed_chunk_nodes = [f"chunk:{cid}" for cid in seed_chunk_ids if f"chunk:{cid}" in self.store.g]

        # 2) symbols from query + seeds
        seed_text = "\n".join([m.get("text", "") for (m, _) in seeds])
        symbols = self._extract_symbols_from_text(query + "\n" + seed_text)

        symbol_nodes = [f"symbol:{s}" for s in symbols if f"symbol:{s}" in self.store.g]

        # 3) expand graph
        start = seed_chunk_nodes + symbol_nodes
        expanded_nodes = self._neighbors_hops(start, hops=hops) if start else set()

        # 4) collect chunks from expanded neighborhood
        chunk_nodes = [n for n in expanded_nodes if n.startswith("chunk:")]

        # prioritize: seeds first
        ordered_chunk_nodes = seed_chunk_nodes + [c for c in chunk_nodes if c not in seed_chunk_nodes]

        # build context pack (filtré + priorisé)
        chunks_candidates = []
        for cn in ordered_chunk_nodes:
            cid = cn.split("chunk:")[1]
            meta_item = next((x for x in self.store.meta if x["id"] == cid), None)
            if meta_item:
                chunks_candidates.append(meta_item)

        # fallback utile: si expansion graph vide/pauvre, utiliser aussi seeds directement
        if not chunks_candidates:
            chunks_candidates = [m for (m, _) in seeds]

        chunks_out = self._prioritize_items(chunks_candidates, query, max_items=max_chunks)

        # graph facts (light)
        facts = []
        for s in list(symbols)[:12]:
            sn = f"symbol:{s}"
            if sn in self.store.g:
                try:
                    neigh = list(self.store.g.neighbors(sn))[:8]
                except Exception:
                    neigh = []
                facts.append({"symbol": s, "neighbors": neigh})

        # logs debug utiles
        try:
            lang_guess = self._infer_language_from_query(query)
            print(f"[RAG] language détecté: {lang_guess}")
            print(f"[RAG] Seeds bruts: {len(raw_seeds)} | Seeds filtrés: {len(seeds)} | Chunks retenus: {len(chunks_out)}")
            if chunks_out:
                print("[RAG] Sources retenues (top):")
                for c in chunks_out[:6]:
                    print(f"   - {c.get('source', '')}")
        except Exception:
            pass

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