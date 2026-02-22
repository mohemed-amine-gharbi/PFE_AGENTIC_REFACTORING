# ==================== agents/test_agent.py (version ULTRA-ROBUSTE) ====================

from .base_agent import BaseAgent
from pathlib import Path
import subprocess
import tempfile
import os
import sys
import re


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
        tools = [
            # Python
            "python", "ruff", "black", "mypy", "pytest", "coverage",
            # JS
            "npm", "npx", "node",
            # Java
            "javac", "mvn", "gradle",
            # C/C++
            "gcc", "g++", "make",
            # Go
            "go",
            # Ruby
            "ruby", "rspec"
        ]

        for tool in tools:
            try:
                subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    check=False,
                    timeout=5
                )
                available[tool] = True
            except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
                available[tool] = False

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
                errors="ignore",
                timeout=30
            )
            output = (p.stdout or "") + "\n" + (p.stderr or "")
            return p.returncode, output.strip(), ""
        except FileNotFoundError:
            return -1, "", f"Commande introuvable : {cmd[0]}"
        except subprocess.TimeoutExpired:
            return -1, "", f"Timeout : commande {cmd[0]} trop longue"
        except Exception as e:
            return -1, "", f"Erreur d'exécution : {str(e)}"

    # ------------------------------------------------------------------
    # PYTHON
    # ------------------------------------------------------------------

    def python_syntax(self, filename):
        return self.run(["python", "-m", "py_compile", filename], "python")

    def ruff(self):
        return self.run(["ruff", "check", ".", "--exit-zero"], "ruff")

    def black_check(self):
        return self.run(["black", "--check", "."], "black")

    def mypy(self):
        return self.run(["mypy", "."], "mypy")

    def pytest(self):
        return self.run(
            ["pytest", "-q", "--disable-warnings", "--maxfail=1"],
            "pytest"
        )

    def coverage_pytest(self):
        if not self.available_tools.get("coverage", False):
            return -1, "", "coverage non installé"
        return self.run(
            ["coverage", "run", "-m", "pytest"],
            "coverage"
        )

    # ------------------------------------------------------------------
    # JAVASCRIPT / TYPESCRIPT
    # ------------------------------------------------------------------

    def jest(self):
        return self.run(["npx", "jest", "--passWithNoTests"], "npx")

    # ------------------------------------------------------------------
    # JAVA
    # ------------------------------------------------------------------

    def maven_test(self):
        return self.run(["mvn", "test"], "mvn")

    # ------------------------------------------------------------------
    # GO
    # ------------------------------------------------------------------

    def go_test(self):
        return self.run(["go", "test", "./..."], "go")

    # ------------------------------------------------------------------
    # RUBY
    # ------------------------------------------------------------------

    def rspec(self):
        return self.run(["rspec"], "rspec")


class TestAgent(BaseAgent):
    """
    Agent de validation avec gestion des outils manquants et extraction ultra-robuste.
    """

    def __init__(self, llm):
        super().__init__(llm, name="TestAgent")

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

            # ================= PYTHON =================
            if lang_key == "python":

                # -------- Syntaxe Python --------
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

                    if out:
                        for line in out.split("\n")[:3]:
                            if line.strip():
                                report["summary"].append(f"   → {line.strip()}")

                # -------- Ruff --------
                ret, out, err = tools.ruff()
                if err and "non disponible" in err:
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

                # -------- Black --------
                ret, out, err = tools.black_check()
                if err and "non disponible" in err:
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
                        if report["status"] == "SUCCESS":
                            report["status"] = "WARNING"

                # -------- mypy --------
                ret, out, err = tools.mypy()
                if err and "non disponible" in err:
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
                        if report["status"] == "SUCCESS":
                            report["status"] = "WARNING"

                # -------- Pytest --------
                ret, out, err = tools.pytest()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ pytest non installé - tests unitaires ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "pytest",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tous les tests pytest passent",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests pytest échoués")

            # ================= JAVASCRIPT / TYPESCRIPT =================
            elif lang_key in ["javascript", "typescript"]:

                ret, out, err = tools.jest()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ Jest non installé - tests ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "jest",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tous les tests Jest passent",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests Jest échoués")

            # ================= JAVA =================
            elif lang_key == "java":

                ret, out, err = tools.maven_test()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ Maven non installé - tests ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "maven",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tests Maven réussis",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests Maven échoués")

            # ================= GO =================
            elif lang_key == "go":

                ret, out, err = tools.go_test()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ Go non installé - tests ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "go test",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tests Go réussis",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests Go échoués")

            # ================= RUBY =================
            elif lang_key == "ruby":

                ret, out, err = tools.rspec()
                if err and "non disponible" in err:
                    report["warnings"].append("⚠️ RSpec non installé - tests ignorés")
                else:
                    status = "SUCCESS" if ret == 0 else "FAILED"
                    report["details"].append({
                        "tool": "rspec",
                        "status": status,
                        "return_code": ret,
                        "output": out or "✅ Tests RSpec réussis",
                        "error": err
                    })
                    if ret != 0:
                        report["status"] = "FAILED"
                        report["summary"].append("❌ Tests RSpec échoués")

            # ================= METRICS =================
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
            
            if len(indent_sizes) > 2:
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
            syntax_errors = []
            for detail in analysis.get("details", []):
                if detail.get("tool") == "python_syntax" and detail.get("status") == "FAILED":
                    output = detail.get("output", "")
                    if output:
                        lines = output.split("\n")
                        for line in lines:
                            if "SyntaxError" in line or "Error" in line:
                                syntax_errors.append(line.strip())
            
            if syntax_errors:
                try:
                    print(f"🔄 Tentative de correction de {len(syntax_errors)} erreur(s) de syntaxe...")
                    
                    # NOUVEAU PROMPT ULTRA-STRICT
                    prompt = f"""INSTRUCTIONS CRITIQUES - SUIVEZ EXACTEMENT:

1. Vous DEVEZ retourner UNIQUEMENT du code Python
2. AUCUN texte explicatif AVANT le code
3. AUCUN texte explicatif APRÈS le code
4. PAS de "Here's", "Voici", "Le code", etc.
5. PAS de numéros (1., 2., 3., etc.)
6. PAS de markdown (```python)
7. Commencez DIRECTEMENT par import, def, class, ou du code Python

Erreurs à corriger:
{chr(10).join(syntax_errors[:3])}

CODE À CORRIGER (corrigez SEULEMENT la syntaxe):
{code}

RETOURNEZ UNIQUEMENT LE CODE PYTHON CORRIGÉ (première ligne doit être du code):"""
                    
                    corrected_code = self.llm.ask(
                        system_prompt="Vous êtes un correcteur de syntaxe. Retournez UNIQUEMENT du code Python. AUCUNE explication. Première ligne = code Python.",
                        user_prompt=prompt,
                        temperature=0.05  # Ultra-bas
                    )
                    
                    # EXTRACTION ULTRA-ROBUSTE
                    corrected_code = self._extract_pure_code(corrected_code)
                    
                    if corrected_code and corrected_code != code:
                        # Vérifier que c'est du vrai code
                        if self._is_valid_python_code(corrected_code):
                            corrected_analysis = self.analyze(corrected_code, language)
                            if corrected_analysis["status"] != "FAILED":
                                code = corrected_code
                                analysis = corrected_analysis
                                analysis["summary"].insert(0, "✅ Erreurs de syntaxe corrigées automatiquement")
                            else:
                                print("⚠️ Le code corrigé a encore des erreurs")
                                analysis["summary"].append("⚠️ Correction automatique échouée")
                        else:
                            print("⚠️ Le LLM n'a pas retourné du code Python valide")
                            analysis["summary"].append("⚠️ LLM n'a pas retourné du code valide")
                    
                except Exception as e:
                    print(f"⚠️ Échec de la correction: {e}")
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
    
    def _extract_pure_code(self, response):
        """
        EXTRACTION ULTRA-ROBUSTE avec 5 méthodes successives.
        """
        original_response = response
        
        # MÉTHODE 1: Enlever tout le texte explicatif ligne par ligne
        lines = response.split("\n")
        code_lines = []
        code_started = False
        
        # Patterns à ignorer (AUGMENTÉS)
        ignore_patterns = [
            r"^here'?s?\s+",
            r"^voici\s+",
            r"^le code",
            r"^the code",
            r"^corrected",
            r"^corrigé",
            r"^refactored",
            r"^improved",
            r"^\d+\.",  # Numéros de liste
            r"^[-*]\s+",  # Puces
            r"^this\s+",
            r"^note:",
            r"^explanation",
            r"^i've",
            r"^addresses",
            r"^variable names",
        ]
        
        for line in lines:
            stripped = line.strip()
            stripped_lower = stripped.lower()
            
            # Ignorer les lignes vides au début
            if not code_started and not stripped:
                continue
            
            # Ignorer les lignes markdown
            if stripped in ["```python", "```py", "```", "python", "py"]:
                continue
            
            # Ignorer les lignes explicatives
            if not code_started:
                should_ignore = False
                for pattern in ignore_patterns:
                    if re.match(pattern, stripped_lower):
                        should_ignore = True
                        break
                
                if should_ignore:
                    continue
                
                # Détecter le VRAI début du code
                if self._line_is_python_code(line):
                    code_started = True
                    code_lines.append(line)
            else:
                # Une fois commencé, prendre tout SAUF les explications de fin
                should_stop = False
                for pattern in ignore_patterns:
                    if re.match(pattern, stripped_lower):
                        should_stop = True
                        break
                
                if should_stop:
                    break
                
                code_lines.append(line)
        
        result = "\n".join(code_lines).strip()
        
        # MÉTHODE 2: Chercher les blocs markdown
        if not result or not self._is_valid_python_code(result):
            markdown_match = re.search(r'```(?:python|py)?\n(.*?)```', response, re.DOTALL)
            if markdown_match:
                result = markdown_match.group(1).strip()
        
        # MÉTHODE 3: Enlever tout avant "import", "def", "class", "from"
        if not result or not self._is_valid_python_code(result):
            for keyword in ["import ", "from ", "def ", "class "]:
                if keyword in response:
                    idx = response.find(keyword)
                    result = response[idx:].strip()
                    break
        
        # MÉTHODE 4: Enlever les numéros de lignes si présents
        if result:
            result = re.sub(r'^\d+[\.:]\s*', '', result, flags=re.MULTILINE)
        
        # MÉTHODE 5: Si tout échoue, retourner l'original
        if not result or len(result) < 10:
            print("⚠️ Extraction échouée, retour à l'original")
            return original_response
        
        return result
    
    def _line_is_python_code(self, line):
        """Vérifie si UNE ligne est du code Python"""
        stripped = line.strip()
        if not stripped:
            return False
        
        # Mots-clés Python qui commencent du code
        python_starters = [
            "import ", "from ", "def ", "class ", "@",
            "if ", "elif ", "else:", "for ", "while ",
            "with ", "try:", "except ", "finally:",
            "return ", "yield ", "raise ", "assert ",
            "print(", "len(", "str(", "int(", "float(",
            "#", '"""', "'''",
        ]
        
        # Variables CUSTOMERS, etc.
        if re.match(r'^[A-Z_]+\s*=', stripped):
            return True
        
        return any(stripped.startswith(starter) for starter in python_starters)
    
    def _is_valid_python_code(self, code):
        """
        Vérifie si le code est du Python valide (pas juste du texte).
        """
        if not code or len(code.strip()) < 5:
            return False
        
        lines = [l.strip() for l in code.split("\n") if l.strip()]
        if not lines:
            return False
        
        first_line = lines[0]
        
        # DOIT commencer par du code Python
        if not self._line_is_python_code(first_line):
            return False
        
        # NE DOIT PAS contenir de texte explicatif
        bad_phrases = [
            "here's", "voici", "refactored", "improved",
            "addresses the", "i've made", "explanation"
        ]
        
        first_20_chars = first_line[:20].lower()
        if any(phrase in first_20_chars for phrase in bad_phrases):
            return False
        
        # Au moins 30% des lignes doivent être du code
        code_line_count = sum(1 for line in lines if self._line_is_python_code(line))
        code_ratio = code_line_count / len(lines)
        
        return code_ratio >= 0.3