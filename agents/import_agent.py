from agents.base_agent import BaseAgent
import re

class ImportAgent(BaseAgent):
    """
    Agent qui détecte et propose d'optimiser les imports inutilisés ou dupliqués.
    """
    def __init__(self, llm):
        super().__init__(llm, name="ImportAgent")

    def analyze(self, code, language):
        if language == "Python":
            imports = re.findall(r'^\s*(import .+|from .+ import .+)', code, flags=re.MULTILINE)
            used_imports = []
            for imp in imports:
                name_match = re.findall(r'import (\w+)', imp)
                for name in name_match:
                    if name in code:
                        used_imports.append(imp)
            unused_imports = list(set(imports) - set(used_imports))
            return unused_imports
        else:
            return ["LLM import analysis needed"]

    def apply(self, code, language):
        analysis = self.analyze(code, language)
        if analysis:
            prompt = (
                f"Refactor the following {language} code by removing unused imports: {analysis}. "
                "Keep functionality unchanged."
            )
            proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)
        else:
            proposal = code
        return {"name": self.name, "analysis": analysis, "proposal": proposal}
