class BaseAgent:
    """
    Classe de base pour tous les agents.
    Fournit une interface commune pour analyze et apply.
    """
    def __init__(self, llm, name="Agent inconnu"):
        self.llm = llm
        self.name = name

    def analyze(self, code, language):
        """
        Analyse le code et retourne une liste de problèmes ou suggestions.
        Doit être surchargée par chaque agent.
        """
        return []

    def apply(self, code, language):
        """
        Applique l'analyse sur le code et retourne le résultat.
        Chaque agent peut renvoyer:
        {
            "name": self.name,
            "analysis": [...],
            "proposal": "nouvelle version du code"
        }
        """
        analysis = self.analyze(code, language)
        if analysis:
            # Prompt spécifique à l'agent, à surcharger si nécessaire
            prompt = f"Refactor code for {self.name} improvements in {language}."
            proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)
        else:
            proposal = code
        return {"name": self.name, "analysis": analysis, "proposal": proposal}
