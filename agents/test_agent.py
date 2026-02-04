# ==================== agents/test_agent.py (version améliorée) ====================

from .base_agent import BaseAgent
from pathlib import Path
import subprocess
import tempfile
import os
import sys


class StaticTools:
    """
    Outils d'analyse statique avec gestion des erreurs d'installation.
    """
    def __init__(self, repo_path: Path, language: str):
        self.repo_path = repo_path
        self.language = language.lower()
        self.available_tools = self._detect_available_tools()

    def _detect_available_tools(self):
        """Détecte les outils disponibles sur le système"""
        available = {}
        
        # Vérifier les outils Python
        python_tools = ["ruff", "black", "mypy", "pylint"]
        for tool in python_tools:
            try:
                subprocess.run([tool, "--version"], 
                              capture_output=True, 
                              check=False)
                available[tool] = True
            except (FileNotFoundError, OSError):
                available[tool] = False
        
        # Vérifier les compilateurs
        compilers = {
            "python": "python",
            "java": "javac",
            "gcc": "gcc",
            "g++": "g++",
            "go": "go",
            "ruby": "ruby",
            "node": "node",
            "npm": "npm"
        }
        
        for name, cmd in compilers.items():
            try:
                subprocess.run([cmd, "--version"] if cmd != "python" else [cmd, "--version"],
                              capture_output=True,
                              check=False)
                available[name] = True
            except (FileNotFoundError, OSError):
                available[name] = False
        
        return available

    def run(self, cmd, tool_name=None):
        """
        Exécute une commande avec gestion d'erreur améliorée.
        
        Returns:
            tuple: (status_code, output, error_message)
        """
        # Vérifier si l'outil est disponible
        if tool_name and not self.available_tools.get(tool_name, False):
            return -1, "", f"Outil '{tool_name}' non disponible. Installez-le d'abord."
        
        try:
            p = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            output = (p.stdout or "") + "\n" + (p.stderr or "")
            return p.returncode, output.strip(), ""
        except FileNotFoundError:
            return -1, "", f"Commande introuvable : {cmd[0]}"
        except Exception as e:
            return -1, "", f"Erreur d'exécution : {str(e)}"

    def python_syntax(self, filename):
        """Vérifie la syntaxe Python (toujours disponible)"""
        return self.run(["python", "-m", "py_compile", filename], "python")

    def ruff(self):
        """Exécute Ruff si disponible"""
        if self.available_tools.get("ruff", False):
            return self.run(["ruff", "check", ".", "--exit-zero"], "ruff")
        return -1, "", "Ruff non installé. Installez avec: pip install ruff"

    def black_check(self):
        """Vérifie le formatage avec Black si disponible"""
        if self.available_tools.get("black", False):
            return self.run(["black", "--check", "."], "black")
        return -1, "", "Black non installé. Installez avec: pip install black"

    def mypy(self):
        """Vérification de types avec mypy si disponible"""
        if self.available_tools.get("mypy", False):
            return self.run(["mypy", "."], "mypy")
        return -1, "", "mypy non installé. Installez avec: pip install mypy"


class TestAgent(BaseAgent):
    """
    Agent de validation avec gestion des outils manquants.
    """

    def __init__(self, llm):
        super().__init__(llm, name="TestAgent")
        self.supported_languages = {
            "python": ["python_syntax", "ruff", "black_check", "mypy"],
            "javascript": [],
            "typescript": [],
            "java": [],
            "c": [],
            "cpp": [],
            "go": [],
            "ruby": [],
        }

    def analyze(self, code, language):
        """
        Analyse le code avec gestion élégante des outils manquants.
        """
        lang_key = language.lower()
        report = {
            "status": "SUCCESS",
            "summary": [],
            "details": [],
            "warnings": [],
            "metrics": {},
            "tools_available": True
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            
            # Déterminer l'extension
            extensions = {
                "python": ".py",
                "javascript": ".js", 
                "typescript": ".ts",
                "java": ".java",
                "c": ".c",
                "cpp": ".cpp",
                "go": ".go",
                "ruby": ".rb"
            }
            
            ext = extensions.get(lang_key, ".py")
            filename = f"test_code{ext}"
            file_path = path / filename
            
            # Écrire le code
            file_path.write_text(code, encoding="utf-8")
            
            # Initialiser les outils
            tools = StaticTools(path, language)
            
            # Vérification syntaxique BASIQUE (toujours disponible)
            if lang_key == "python":
                ret, out, err = tools.python_syntax(filename)
                status = "SUCCESS" if ret == 0 else "FAILED"
                detail = {
                    "tool": "python_syntax",
                    "status": status,
                    "return_code": ret,
                    "output": out or "Syntaxe Python valide",
                    "error": err
                }
                
                if err:
                    detail["suggestion"] = "Utilisez 'python -m py_compile fichier.py' pour vérifier manuellement"
                
                report["details"].append(detail)
                
                if ret != 0:
                    report["status"] = "FAILED"
                    report["summary"].append("❌ Erreur de syntaxe Python détectée")
                    
                    # Afficher l'erreur de syntaxe de manière lisible
                    if out:
                        error_lines = out.split("\n")
                        for line in error_lines[:3]:  # Afficher seulement les 3 premières lignes
                            if line.strip():
                                report["summary"].append(f"   → {line.strip()}")
            
            # Outils optionnels (avec gestion d'absence)
            if lang_key == "python":
                # Ruff
                ret, out, err = tools.ruff()
                if err and "non installé" in err:
                    report["warnings"].append("⚠️ Ruff non installé - impossible de vérifier le style")
                    report["tools_available"] = False
                else:
                    status = "SUCCESS" if ret == 0 else "WARNING"
                    report["details"].append({
                        "tool": "ruff",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Aucun problème de style détecté",
                        "error": err
                    })
                    if ret != 0:
                        report["summary"].append("⚠️ Problèmes de style détectés (Ruff)")
                        if report["status"] == "SUCCESS":
                            report["status"] = "WARNING"
                
                # Black
                ret, out, err = tools.black_check()
                if err and "non installé" in err:
                    report["warnings"].append("⚠️ Black non installé - impossible de vérifier le formatage")
                else:
                    status = "SUCCESS" if ret == 0 else "WARNING"
                    report["details"].append({
                        "tool": "black",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Formatage correct (Black)",
                        "error": err
                    })
                    if ret != 0:
                        report["warnings"].append("Code nécessite un reformatage avec Black")
                
                # mypy
                ret, out, err = tools.mypy()
                if err and "non installé" in err:
                    report["warnings"].append("⚠️ mypy non installé - impossible de vérifier les types")
                else:
                    status = "SUCCESS" if ret == 0 else "WARNING"
                    report["details"].append({
                        "tool": "mypy",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Aucune erreur de type",
                        "error": err
                    })
                    if ret != 0:
                        report["warnings"].append("Problèmes de typage détectés")
            
            # Calculer les métriques de base (toujours disponibles)
            self._calculate_basic_metrics(code, report, lang_key)
        
        return report

    def _calculate_basic_metrics(self, code, report, language):
        """Calcule les métriques de base sans outils externes"""
        lines = code.splitlines()
        non_empty_lines = [l for l in lines if l.strip()]
        
        report["metrics"] = {
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty_lines),
            "characters": len(code),
            "average_line_length": sum(len(l) for l in lines) / max(1, len(lines))
        }
        
        # Détecter les problèmes évidents
        warnings = []
        
        # Lignes trop longues
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            warnings.append(f"Lignes trop longues (>120 chars): {long_lines[:3]}")
        
        # Indentation incohérente (Python)
        if language == "python":
            indent_sizes = set()
            for line in non_empty_lines:
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    if indent > 0:
                        indent_sizes.add(indent)
            
            if len(indent_sizes) > 2:  # Plus de 2 tailles d'indentation différentes
                warnings.append("Indentation incohérente détectée")
        
        if warnings:
            report["warnings"].extend(warnings)

    def apply(self, code, language, temperature=None):
        """
        Applique l'analyse avec correction automatique si erreurs de syntaxe.
        """
        analysis = self.analyze(code, language)
        
        # Si erreur de syntaxe et LLM disponible, essayer de corriger
        if analysis["status"] == "FAILED" and hasattr(self.llm, 'ask'):
            # Chercher les erreurs de syntaxe
            syntax_errors = []
            for detail in analysis.get("details", []):
                if detail.get("tool") == "python_syntax" and detail.get("status") == "FAILED":
                    output = detail.get("output", "")
                    if output:
                        # Extraire l'erreur de syntaxe
                        lines = output.split("\n")
                        for line in lines:
                            if "SyntaxError" in line or "Error" in line:
                                syntax_errors.append(line.strip())
            
            if syntax_errors:
                try:
                    print(f"🔄 Tentative de correction de {len(syntax_errors)} erreur(s) de syntaxe...")
                    
                    prompt = f"""
Le code Python suivant a des erreurs de syntaxe. 
Corrige UNIQUEMENT les erreurs de syntaxe, ne change pas la logique.
Retourne SEULEMENT le code Python corrigé.

Erreurs détectées:
{chr(10).join(f'- {err}' for err in syntax_errors[:3])}

Code avec erreurs:
{code}
"""
                    
                    corrected_code = self.llm.ask(
                        system_prompt="Expert en correction de syntaxe Python. Ne change que ce qui est nécessaire pour corriger les erreurs de syntaxe.",
                        user_prompt=prompt,
                        temperature=0.1  # Très bas pour la précision
                    )
                    
                    # Nettoyer le code corrigé
                    corrected_code = self._clean_llm_response(corrected_code)
                    
                    # Vérifier si le code corrigé est différent
                    if corrected_code and corrected_code != code:
                        # Réanalyser
                        corrected_analysis = self.analyze(corrected_code, language)
                        if corrected_analysis["status"] != "FAILED":
                            code = corrected_code
                            analysis = corrected_analysis
                            analysis["summary"].insert(0, "✅ Erreurs de syntaxe corrigées automatiquement")
                            analysis["summary"].append("🔧 Correction par LLM avec température=0.1")
                        else:
                            analysis["summary"].append("⚠️ Correction automatique échouée - erreurs persistantes")
                    
                except Exception as e:
                    print(f"⚠️ Échec de la correction automatique: {e}")
                    analysis["summary"].append("❌ Correction automatique impossible")
        
        return {
            "name": self.name,
            "status": analysis.get("status", "N/A"),
            "summary": analysis.get("summary", []),
            "details": analysis.get("details", []),
            "warnings": analysis.get("warnings", []),
            "metrics": analysis.get("metrics", {}),
            "tools_available": analysis.get("tools_available", True),
            "proposal": code,
            "temperature_used": temperature if temperature is not None else "N/A"
        }
    
    def _clean_llm_response(self, response):
        """Nettoie la réponse du LLM pour extraire uniquement le code"""
        # Supprimer les backticks
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                # Prendre le contenu entre les premiers backticks
                response = parts[1]
                # Enlever le langage spécificateur
                if response.startswith("python\n"):
                    response = response[7:]
        
        # Supprimer le texte explicatif avant le code
        lines = response.splitlines()
        code_lines = []
        code_started = False
        
        for line in lines:
            stripped = line.strip()
            if not code_started:
                if stripped.startswith(("import", "def", "class", "from", "@")):
                    code_started = True
                    code_lines.append(line)
                elif stripped and not stripped.startswith(("# ", "// ")):
                    # Si c'est du code sans mot-clé évident
                    code_started = True
                    code_lines.append(line)
            else:
                code_lines.append(line)
        
        return "\n".join(code_lines) if code_lines else response