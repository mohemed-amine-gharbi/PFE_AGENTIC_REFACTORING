class BaseAgent:
    """
    Classe de base pour tous les agents avec support de température rétrocompatible.
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
    
    def apply(self, code, language, temperature=None):
        """
        Applique l'analyse sur le code.
        
        Args:
            code: Code source
            language: Langage de programmation
            temperature: Température LLM (optionnel, rétrocompatible)
            
        Returns:
            dict: Résultat standardisé
        """
        analysis = self.analyze(code, language)
        
        if analysis:
            # Vérifier si la méthode llm.ask supporte temperature
            llm_method = getattr(self.llm, 'ask', None)
            if not callable(llm_method):
                raise AttributeError(f"LLM client {self.llm} n'a pas de méthode 'ask'")
            
            # Construire le prompt (méthode peut être surchargée)
            prompt = self.build_prompt(code, language)
            
            try:
                # Essayer d'appeler avec température si supporté
                if temperature is not None and hasattr(self.llm, 'ask'):
                    # Vérifier la signature de la méthode
                    import inspect
                    sig = inspect.signature(self.llm.ask)
                    params = sig.parameters
                    
                    if 'temperature' in params:
                        proposal = self.llm.ask(
                            system_prompt=prompt,
                            user_prompt=code,
                            temperature=temperature
                        )
                    else:
                        # Fallback sans température
                        proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)
                else:
                    proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)
                    
            except Exception as e:
                # En cas d'erreur, utiliser le code original
                print(f"⚠️ Erreur LLM pour {self.name}: {e}")
                proposal = code
        else:
            proposal = code
        
        # Retourner le résultat standardisé
        result = {
            "name": self.name,
            "analysis": analysis,
            "proposal": proposal
        }
        
        # Ajouter la température utilisée si disponible
        if temperature is not None:
            result["temperature_used"] = temperature
        
        return result
    
    def build_prompt(self, code, language):
        """Méthode par défaut pour construire le prompt (peut être surchargée)"""
        return f"Refactor the following {language} code for {self.name} improvements."