# ==================== agents/patch_agent.py (version corrigée) ====================

from .base_agent import BaseAgent
import re


class PatchAgent(BaseAgent):
    """
    Agent de nettoyage avancé avec validation de syntaxe.
    """

    def __init__(self, llm):
        super().__init__(llm, name="PatchAgent")
        self.changes_applied = []

    def analyze(self, code, language):
        """Détecte les problèmes de formatage"""
        issues = []
        self.changes_applied = []  # Réinitialiser

        # Détection de markdown
        if "```" in code:
            issues.append({"type": "markdown", "note": "Blocs Markdown détectés"})

        # Détection de texte explicatif
        lines = code.splitlines()
        code_started = False
        non_code_lines = []

        for i, line in enumerate(lines[:10]):  # Vérifier les 10 premières lignes
            stripped = line.strip()
            if not stripped:
                continue
            if not code_started:
                if stripped.startswith(("import", "def", "class", "from", "function", "public", "private", "const", "let", "var")):
                    code_started = True
                else:
                    non_code_lines.append(f"Ligne {i+1}: {stripped[:50]}...")

        if non_code_lines:
            issues.append({"type": "explanatory_text", "note": f"Texte non-code détecté: {len(non_code_lines)} lignes"})

        if not issues:
            issues.append({"type": "clean", "note": "Code relativement propre"})

        return issues

    def clean_code(self, code, language):
        """
        Nettoie le code sans utiliser le LLM pour éviter les erreurs de syntaxe.
        """
        cleaned_lines = []
        in_code_block = False
        code_started = False

        # Patterns de texte explicatif à ignorer
        EXPLANATORY_PATTERNS = [
            r"^here'?s?\s+",
            r"^voici\s+",
            r"^le code",
            r"^the code",
            r"^corrected",
            r"^corrigé",
            r"^refactored",
            r"^improved",
            r"^\d+\.\s+",   # Listes numérotées : "1. ..."
            r"^[-*]\s+",    # Puces : "- ..." ou "* ..."
            r"^this\s+",
            r"^note:",
            r"^explanation",
            r"^i've",
        ]

        PYTHON_STARTERS = (
            "import ", "from ", "def ", "class ", "@",
            "if ", "elif ", "else:", "for ", "while ",
            "with ", "try:", "except", "finally:",
            "return ", "yield ", "raise ", "assert ",
            "print(", "#", '"""', "'''",
        )

        for line in code.splitlines():
            stripped = line.strip()

            # --- Gestion des blocs markdown ---
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue

            # À l'intérieur d'un bloc markdown : garder la ligne
            if in_code_block:
                if stripped:
                    code_started = True
                cleaned_lines.append(line)
                continue

            # Hors bloc markdown : filtrer le texte explicatif
            if not stripped:
                if code_started:  # Garder les lignes vides APRÈS le début du code
                    cleaned_lines.append(line)
                continue

            stripped_lower = stripped.lower()

            # Ignorer les lignes explicatives
            is_explanatory = any(re.match(p, stripped_lower) for p in EXPLANATORY_PATTERNS)
            if is_explanatory:
                continue

            # Vérifier si c'est une vraie ligne de code
            is_code = (
                stripped.startswith(PYTHON_STARTERS)
                or re.match(r'^[A-Z_][A-Z_0-9]*\s*=', stripped)   # Constantes
                or re.match(r'^[a-z_]\w*\s*[=(]', stripped)        # Variables/appels
                or re.match(r'^\s', line)                           # Ligne indentée
            )

            if is_code:
                code_started = True
                cleaned_lines.append(line)
            elif code_started:
                pass  # On drop silencieusement

        cleaned_code = "\n".join(cleaned_lines)

        # --- Nettoyage des commentaires inline Python ---
        if language.lower() == "python":
            final_lines = []
            for line in cleaned_code.splitlines():
                hash_pos = line.find("#")
                if hash_pos != -1:
                    before = line[:hash_pos]
                    if before.count('"') % 2 == 0 and before.count("'") % 2 == 0:
                        line = line[:hash_pos].rstrip()
                if line.strip():
                    final_lines.append(line)
            cleaned_code = "\n".join(final_lines)

        return cleaned_code

    def apply(self, code, language, temperature=None):
        """Applique le nettoyage avec validation syntaxique"""
        analysis = self.analyze(code, language)
        self.changes_applied = []

        # Nettoyer le code (sans LLM pour éviter les erreurs)
        cleaned_code = self.clean_code(code, language)
        self.changes_applied.append("Texte explicatif et markdown supprimés")

        # VALIDATION CRITIQUE : Vérifier la syntaxe Python
        if language.lower() == "python":
            try:
                import ast
                ast.parse(cleaned_code)
                self.changes_applied.append("Syntaxe Python validée")
            except SyntaxError as e:
                print(f"⚠️ Erreur de syntaxe après nettoyage: {e}")
                lines = cleaned_code.splitlines()
                valid_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("# "):
                        valid_lines.append(line)
                cleaned_code = "\n".join(valid_lines)
                self.changes_applied.append(f"Erreur de syntaxe corrigée: {e}")

        return {
            "name": self.name,
            "analysis": analysis,
            "proposal": cleaned_code,
            "changes_applied": self.changes_applied,
            "temperature_used": temperature if temperature is not None else "N/A"
        }