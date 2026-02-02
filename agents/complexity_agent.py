from agents.base_agent import BaseAgent

class ComplexityAgent(BaseAgent):
    def __init__(self, llm):
        self.llm = llm
        self.name = "ComplexityAgent"

    def build_prompt(self, code, language):
        return (
            f"Analyse ce code {language} et propose un refactoring pour réduire la complexité algorithmique. "
            "Si possible, transforme les boucles imbriquées ou opérations coûteuses pour améliorer l'efficacité. "
            "Retourne uniquement le code refactoré."
        )

    def analyze(self, code):
        # Analyse simplifiée: détecte les boucles imbriquées
        nested_loops = [line for line in code.splitlines() if "for" in line or "while" in line]
        return nested_loops

    def apply(self, code, language, temperature=None):
        analysis = self.analyze(code)
        if analysis:
            prompt = self.build_prompt(code, language)
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