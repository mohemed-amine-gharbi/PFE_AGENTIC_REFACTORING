from agents.base_agent import BaseAgent
import re

class RenameAgent(BaseAgent):
    def __init__(self, llm):
        self.llm = llm
        self.name = "RenameAgent"

    def analyze(self, code):
        """
        Identifie toutes les variables simples à une lettre dans le code
        et renvoie la liste de ces variables pour l'analyse.
        """
        # Cherche toutes les variables d'une seule lettre (a-z)
        variables = sorted(set(re.findall(r'\b([a-z])\b', code)))
        return variables if variables else []

    def apply(self, code):
        """
        Renomme les variables identifiées avec des noms plus clairs via le LLM
        et renvoie un dictionnaire contenant le nom de l'agent, l'analyse et le code refactoré.
        """
        variables = self.analyze(code)
        analysis = f"Variables identifiées pour renaming : {', '.join(variables)}" if variables else "Aucune variable à renommer"

        if variables:
            # Préparer le prompt pour le LLM
            system_prompt = "Tu es un assistant Python expert en refactoring."
            user_prompt = (
                f"Voici le code :\n{code}\n"
                "Propose un dictionnaire Python pour renommer les variables simples à une lettre "
                "en noms significatifs. Exemple: {'a': 'value_a', 'b': 'value_b'}"
            )

            # Appel LLM
            response = self.llm.ask(system_prompt=system_prompt, user_prompt=user_prompt)

            try:
                rename_map = eval(response)  # convertir la réponse LLM en dict
            except Exception:
                # fallback si LLM ne renvoie pas un dict valide
                rename_map = {v: f"var_{v}" for v in variables}

            # Appliquer le renommage dans le code
            new_code = code
            for old, new in rename_map.items():
                new_code = re.sub(rf'\b{old}\b', new, new_code)
        else:
            new_code = code

        return {
            "name": self.name,
            "analysis": analysis,
            "proposal": new_code
        }
