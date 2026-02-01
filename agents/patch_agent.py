from .base_agent import BaseAgent
import re

class PatchAgent(BaseAgent):
    """
    Agent de nettoyage avancé.
    Supprime :
        - Texte explicatif généré par le LLM avant le code
        - Markdown (``` et language blocks)
        - Commentaires inline (#, //)
    Conserve tout le code valide pour le langage spécifié.
    """

    def __init__(self, llm):
        super().__init__(llm, name="PatchAgent")

    def analyze(self, code, language):
        issues = []
        if "```" in code:
            issues.append("Présence de blocs Markdown ```")
        first_line = code.splitlines()[0].strip() if code.splitlines() else ""
        if not first_line.startswith(("import", "def", "class")):
            issues.append("Texte explicatif détecté avant le code")
        if not issues:
            issues.append("Aucun problème évident détecté")
        return issues

    def remove_markdown_and_explanations(self, code):
        # Supprime les blocs ```...```
        code = re.sub(r"```.*?```", "", code, flags=re.DOTALL)

        # Supprime le texte avant la première ligne de code réelle
        lines = code.splitlines()
        cleaned_lines = []
        code_started = False
        for line in lines:
            stripped = line.strip()
            if not code_started:
                if stripped.startswith(("import", "def", "class", "from")):
                    code_started = True
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

    def remove_inline_comments(self, code, language):
        # Détermine le symbole de commentaire selon le langage
        if language.lower() == "python":
            comment_symbols = ["#"]
        elif language.lower() in ["javascript", "typescript", "java", "c", "cpp", "c#", "go", "ruby"]:
            comment_symbols = ["//"]
        else:
            comment_symbols = []

        lines = code.splitlines()
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if comment_symbols:
                min_index = len(line)
                for symbol in comment_symbols:
                    idx = line.find(symbol)
                    if idx != -1:
                        # Ignore les URLs contenant http:// ou https://
                        if "http://" in line or "https://" in line:
                            continue
                        if idx < min_index:
                            min_index = idx
                cleaned_line = line[:min_index].rstrip() if min_index != len(line) else line
                if cleaned_line.strip() != "":
                    cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def apply(self, code, language):
        analysis = self.analyze(code, language)

        # 1️⃣ Supprime Markdown et texte explicatif
        code = self.remove_markdown_and_explanations(code)

        # 2️⃣ Supprime les commentaires inline
        code = self.remove_inline_comments(code, language)

        # 3️⃣ Optionnel : LLM pour nettoyage final (ne modifie pas la logique)
        prompt = f"""
Tu es un agent de correction.
Retourne UNIQUEMENT du code {language} valide.
Supprime tout texte explicatif, Markdown et commentaires inline.
Ne modifie pas la logique métier.

Code :
{code}
"""
        patched_code = self.llm.ask(system_prompt="Code Patcher", user_prompt=prompt)

        return {
            "name": self.name,
            "analysis": analysis,
            "proposal": patched_code
        }
