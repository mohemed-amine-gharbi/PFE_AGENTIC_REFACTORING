from .base_agent import BaseAgent
from pathlib import Path
import subprocess
import tempfile


class StaticTools:
    """
    Outils d'analyse statique pour Python.
    """
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def run(self, cmd):
        try:
            p = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            out = (p.stdout or "") + "\n" + (p.stderr or "")
            return p.returncode, out.strip()
        except FileNotFoundError:
            return -1, f"Outil introuvable : {cmd[0]}"

    def python_syntax(self, filename):
        return self.run(["python", "-m", "py_compile", filename])

    def ruff(self):
        return self.run(["ruff", "check", "."])


class TestAgent(BaseAgent):
    """
    Agent de validation post-patch.
    """

    def __init__(self, llm):
        super().__init__(llm, name="TestAgent")

    def analyze(self, code, language):
        report = {
            "status": "SUCCESS",
            "summary": [],
            "details": []
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            filename = "temp.py"
            file_path = path / filename
            file_path.write_text(code, encoding="utf-8")

            tools = StaticTools(path)

            # Vérification syntaxe Python
            ret, out = tools.python_syntax(filename)
            report["details"].append({
                "tool": "py_compile",
                "status": ret,
                "output": out or "Syntaxe Python valide"
            })
            if ret != 0:
                report["status"] = "FAILED"
                report["summary"].append("Erreur de syntaxe Python")
                return report

            # Ruff
            ret, out = tools.ruff()
            report["details"].append({
                "tool": "ruff",
                "status": ret,
                "output": out or "Aucun problème Ruff détecté"
            })
            if ret != 0:
                report["status"] = "FAILED"
                report["summary"].append("Problèmes Ruff détectés")
            else:
                report["summary"].append("Code valide et propre")

        return report

    def apply(self, code, language):
        analysis = self.analyze(code, language)
        return {
            "name": self.name,
            "status": analysis.get("status", "N/A"),
            "summary": analysis.get("summary", []),
            "details": analysis.get("details", []),
            "proposal": code
        }
