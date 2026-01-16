import subprocess

class OllamaLLMClient:
    def __init__(self, model_name="mistral:latest"):
        self.model_name = model_name

    def ask(self, system_prompt, user_prompt):
        """
        Envoie le prompt au modèle Ollama local et récupère la réponse.
        """
        full_prompt = system_prompt + "\n" + user_prompt
        try:
            process = subprocess.Popen(
                ["ollama", "run", self.model_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )
            stdout, stderr = process.communicate(full_prompt)

            if process.returncode != 0:
                return f"Error: {stderr.strip()}"

            return stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"
