# agents/base_agent.py

from __future__ import annotations

import inspect

# GraphRAG: import optionnel (fallback si le module n'existe pas)
try:
    from core.graphrag_retriever import GraphRAGRetriever
except Exception:
    GraphRAGRetriever = None


class BaseAgent:
    """
    Classe de base pour tous les agents avec support de température rétrocompatible
    + GraphRAG (optionnel) pour enrichir le contexte.

    GraphRAG est activé uniquement pour les agents de refactoring structurel/sémantique.
    """

    # ✅ RAG seulement pour ces 5 agents
    GRAPHRAG_ENABLED_AGENTS = {
        "RenameAgent",
        "ComplexityAgent",
        "DuplicationAgent",
        "ImportAgent",
        "LongFunctionAgent",
    }

    def __init__(self, llm, name: str = "Agent inconnu", use_graphrag: bool = True):
        self.llm = llm
        self.name = name
        self.use_graphrag = use_graphrag

    def analyze(self, code, language):
        """
        Analyse le code et retourne une liste de problèmes ou suggestions.
        Doit être surchargée par chaque agent.
        """
        return []

    def build_prompt(self, code, language):
        """Méthode par défaut pour construire le prompt (peut être surchargée)"""
        return f"Refactor the following {language} code for {self.name} improvements."

    def _should_use_graphrag(self) -> bool:
        """
        Décide automatiquement si GraphRAG doit être utilisé pour cet agent.
        """
        return (
            self.use_graphrag
            and self.name in self.GRAPHRAG_ENABLED_AGENTS
            and GraphRAGRetriever is not None
        )

    def _inject_graphrag(self, system_prompt: str, code: str, language: str) -> str:
        """
        Injecte un contexte GraphRAG dans le prompt système.
        Si GraphRAG n'est pas disponible, non autorisé pour cet agent, ou échoue,
        retourne system_prompt inchangé.
        """
        if not self._should_use_graphrag():
            return system_prompt

        try:
            retriever = GraphRAGRetriever()
            query = (
                f"Refactoring context for agent={self.name}, language={language}. "
                f"Project conventions, related modules/classes/functions, dependencies. "
                f"Code snippet: {code[:600]}"
            )

            pack = retriever.retrieve(query=query, k_seeds=4, hops=2, max_chunks=6)
            context_txt = retriever.format_context(pack).strip()

            if not context_txt:
                return system_prompt

            # Debug utile (tu peux le garder)
            print(f"🔎 GraphRAG injecté pour {self.name}")

            return (
                system_prompt
                + "\n\n"
                + context_txt
                + "\n\n"
                + "### Usage Rules\n"
                + "- Use retrieved context ONLY if relevant.\n"
                + "- Preserve exact behavior and public APIs.\n"
                + "- If context conflicts with code semantics, prefer code semantics.\n"
            )
        except Exception as e:
            # Fallback silencieux (mais log léger utile pour debug)
            print(f"⚠️ GraphRAG ignoré pour {self.name}: {e}")
            return system_prompt

    def apply(self, code, language, temperature=None):
        """
        Applique l'analyse sur le code.

        Args:
            code: Code source
            language: Langage de programmation
            temperature: Température LLM (optionnel, rétrocompatible)

        Returns:
            dict: Résultat standardisé
        """
        analysis = self.analyze(code, language)

        if analysis:
            # Vérifier si la méthode llm.ask supporte temperature
            llm_method = getattr(self.llm, "ask", None)
            if not callable(llm_method):
                raise AttributeError(f"LLM client {self.llm} n'a pas de méthode 'ask'")

            # Construire le prompt (peut être surchargé)
            prompt = self.build_prompt(code, language)

            # ✅ Injecter GraphRAG seulement pour les agents autorisés
            prompt = self._inject_graphrag(prompt, code, language)

            try:
                # Essayer d'appeler avec température si supporté
                if temperature is not None:
                    sig = inspect.signature(self.llm.ask)
                    params = sig.parameters

                    if "temperature" in params:
                        proposal = self.llm.ask(
                            system_prompt=prompt,
                            user_prompt=code,
                            temperature=temperature
                        )
                    else:
                        # Fallback sans température
                        proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)
                else:
                    proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)

            except Exception as e:
                print(f"⚠️ Erreur LLM pour {self.name}: {e}")
                proposal = code
        else:
            proposal = code

        result = {
            "name": self.name,
            "analysis": analysis,
            "proposal": proposal
        }

        if temperature is not None:
            result["temperature_used"] = temperature

        return result