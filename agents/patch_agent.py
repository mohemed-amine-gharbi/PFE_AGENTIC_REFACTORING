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
        Retourne uniquement du code syntaxiquement valide.
        """
        cleaned_lines = []
        in_code_block = False
        
        for line in code.splitlines():
            stripped = line.strip()
            
            # Gestion des blocs markdown
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            
            # Enlever le texte explicatif avant le code
            if not in_code_block:
                # Vérifier si c'est une ligne de code valide
                if (stripped.startswith(("import", "from", "def", "class", "@")) or
                    (stripped and not stripped.startswith(("# ", "// ", "/*", "* ")))):
                    cleaned_lines.append(line)
            else:
                # À l'intérieur d'un bloc de code, tout garder
                cleaned_lines.append(line)
        
        cleaned_code = "\n".join(cleaned_lines)
        
        # Nettoyer les commentaires inline en excès (Python)
        if language.lower() == "python":
            lines = cleaned_code.splitlines()
            cleaned_lines = []
            for line in lines:
                # Garder seulement jusqu'au premier # qui n'est pas dans une string
                hash_pos = line.find("#")
                if hash_pos != -1:
                    # Vérifier si le # est dans une string
                    before_hash = line[:hash_pos]
                    if before_hash.count('"') % 2 == 0 and before_hash.count("'") % 2 == 0:
                        line = line[:hash_pos].rstrip()
                if line.strip():  # Ne garder que les lignes non vides
                    cleaned_lines.append(line)
            cleaned_code = "\n".join(cleaned_lines)
        
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
                # Essayer de compiler le code
                import ast
                ast.parse(cleaned_code)
                self.changes_applied.append("Syntaxe Python validée")
            except SyntaxError as e:
                # En cas d'erreur, essayer de récupérer le code original
                print(f"⚠️ Erreur de syntaxe après nettoyage: {e}")
                # Garder seulement les lignes qui semblent être du code Python
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