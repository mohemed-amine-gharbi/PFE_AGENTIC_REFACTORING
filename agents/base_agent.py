# agents/base_agent.py

from core.temperature_config import TemperatureConfig

class BaseAgent:
    """
    Classe de base pour tous les agents avec support de température.
    """
    def __init__(self, llm, name="Agent inconnu"):
        self.llm = llm
        self.name = name
        # Récupère la température optimale pour cet agent
        self.optimal_temperature = TemperatureConfig.get_temperature(name)
    
    def apply(self, code, language, temperature=None):
        """
        Applique l'analyse avec la température spécifiée.
        Si temperature=None, utilise la température optimale de l'agent.
        """
        analysis = self.analyze(code, language)
        
        if analysis:
            # Utilise la température spécifiée ou l'optimale
            final_temperature = temperature if temperature is not None else self.optimal_temperature
            
            # Prompt spécifique
            prompt = self.build_prompt(code, language)
            
            # Appel LLM avec température
            proposal = self.llm.ask(
                system_prompt=prompt,
                user_prompt=code,
                temperature=final_temperature
            )
        else:
            proposal = code
            
        return {
            "name": self.name,
            "analysis": analysis,
            "proposal": proposal,
            "temperature_used": final_temperature if 'final_temperature' in locals() else None
        }