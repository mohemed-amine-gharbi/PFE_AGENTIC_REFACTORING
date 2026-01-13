class LLMClient:
    def __init__(self, model_name="gpt-like"):
        self.model_name = model_name

    def ask(self, system_prompt, user_prompt):
        """
        Ici tu peux brancher :
        - OpenAI
        - Mistral
        - Llama
        Pour le PFE : version mock INTELLIGENTE
        """

        # === MOCK LLM (acceptable académiquement) ===
        if "duplicate" in user_prompt.lower():
            return "Extract duplicated logic into a new function."

        if "complexity" in user_prompt.lower():
            return "Split nested conditions into smaller helper functions."

        if "long function" in user_prompt.lower():
            return "Break the function into logical sub-functions."

        if "rename" in user_prompt.lower():
            return "Rename function f to process_values."

        return "No refactoring needed."
