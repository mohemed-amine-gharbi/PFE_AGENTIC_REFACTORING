# agents/rename_agent.py - Version corrigée

from agents.base_agent import BaseAgent
import re

class RenameAgent(BaseAgent):
    """
    Agent spécialisé dans le renommage des variables pour améliorer la lisibilité.
    """
    def __init__(self, llm):
        super().__init__(llm, name="RenameAgent")

    def analyze(self, code, language):
        """
        Trouve toutes les variables simples dans le code Python.
        Pour d'autres langages, le prompt sera adapté automatiquement.
        """
        if language == "Python":
            # Regex pour trouver les noms de variables simples
            pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
            tokens = set(re.findall(pattern, code))
            # On filtre les mots-clés Python
            keywords = {
                "def","return","if","elif","else","for","while","in","import","from","as",
                "print","break","continue","class","with","try","except","pass","and","or","not",
                "is","lambda","True","False","None"
            }
            variables = [tok for tok in tokens if tok not in keywords]
            return variables
        else:
            # Pour d'autres langages, on laisse le LLM analyser
            return ["LLM variable analysis needed"]

    def apply(self, code, language, temperature=None):
        """
        Applique le renommage avec contrôle de température optionnel.
        
        Args:
            code: Code source à analyser
            language: Langage de programmation
            temperature: Température pour le LLM (optionnel)
        """
        analysis = self.analyze(code, language)
        if analysis:
            # Prompt très précis pour le renommage
            prompt = (
                f"Refactor the following {language} code by renaming variables "
                f"to meaningful names. Keep functionality unchanged. Variables: {analysis}"
            )
            
            # Appel LLM avec ou sans température
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