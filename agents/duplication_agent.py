from agents.base_agent import BaseAgent

class DuplicationAgent(BaseAgent):
    """
    Agent qui détecte le code dupliqué et propose de le factoriser.
    """
    def __init__(self, llm):
        super().__init__(llm, name="DuplicationAgent")

    def analyze(self, code, language):
        # Ici, on laisse le LLM détecter les duplications complexes
        prompt = (
            f"Analyze the following {language} code and find duplicated code blocks "
            "that can be refactored into functions or loops."
        )
        return [prompt]  # On retourne le prompt comme analyse initiale

    def apply(self, code, language, temperature=None):
        analysis = self.analyze(code, language)
        prompt = (
            f"Refactor the following {language} code by reducing duplication. "
            "Keep functionality unchanged."
        )
        if temperature is not None:
            proposal = self.llm.ask(
                system_prompt=prompt,
                user_prompt=code,
                temperature=temperature
            )
        else:
            proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)
        return {
            "name": self.name, 
            "analysis": analysis, 
            "proposal": proposal,
            "temperature_used": temperature
        }