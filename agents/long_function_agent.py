from agents.base_agent import BaseAgent
import re

class LongFunctionAgent(BaseAgent):
    """
    Agent qui détecte les fonctions trop longues et propose des refactorings.
    """
    def __init__(self, llm):
        super().__init__(llm, name="LongFunctionAgent")

    def analyze(self, code, language):
        if language == "Python":
            functions = re.findall(r'def (\w+)\(.*\):', code)
            long_functions = []
            lines = code.splitlines()
            for func in functions:
                start = next((i for i, line in enumerate(lines) if f'def {func}' in line), None)
                if start is not None:
                    # On compte les lignes jusqu'à la prochaine fonction ou fin du code
                    end = next((i for i, line in enumerate(lines[start+1:], start+start+1) if line.strip().startswith("def ")), len(lines))
                    if end - start > 20:  # seuil de 20 lignes pour considérer "long"
                        long_functions.append(func)
            return long_functions
        else:
            return ["LLM long function analysis needed"]

    def apply(self, code, language, temperature=None):
        analysis = self.analyze(code, language)
        if analysis:
            prompt = (
                f"Refactor the following {language} code. Functions {analysis} are too long. "
                "Split them into smaller functions without changing behavior."
            )
            if temperature is not None:
                proposal = self.llm.ask(
                    system_prompt=prompt,
                    user_prompt=code,
                    temperature=temperature
                )
            else:
                proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)
        else:
            proposal = code
        return {
            "name": self.name, 
            "analysis": analysis, 
            "proposal": proposal,
            "temperature_used": temperature
        }