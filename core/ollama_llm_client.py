# core/ollama_llm_client.py

import subprocess
import json

class OllamaLLMClient:
    def __init__(self, model_name="mistral:latest"):
        self.model_name = model_name
        self.default_temperature = 0.3
    
    def ask(self, system_prompt, user_prompt, temperature=None):
        """
        Envoie le prompt au modèle Ollama local avec contrôle de température.
        
        Args:
            system_prompt: Prompt système définissant le rôle
            user_prompt: Prompt utilisateur avec le code
            temperature: Contrôle de créativité (0.0-1.0)
        
        Returns:
            str: Réponse du modèle
        """
        if temperature is None:
            temperature = self.default_temperature
        
        # Clamp la température dans la plage valide
        temperature = max(0.0, min(1.0, temperature))
        
        # Construire la requête JSON pour Ollama
        request_data = {
            "model": self.model_name,
            "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}",
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2000,  # Nombre maximum de tokens
                "top_p": 0.9,  # Nucleus sampling
                "repeat_penalty": 1.1  # Pénalité pour répétition
            }
        }
        
        try:
            # Utiliser l'API HTTP d'Ollama
            import requests
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=request_data,
                timeout=120  # Timeout de 120 secondes
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            # Fallback sur l'ancienne méthode subprocess
            return self._fallback_ask(system_prompt, user_prompt, temperature)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _fallback_ask(self, system_prompt, user_prompt, temperature):
        """Méthode de fallback utilisant subprocess"""
        full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        
        try:
            # Construire la commande avec température
            command = [
                "ollama", "run",
                self.model_name,
                "--temperature", str(temperature)
            ]
            
            process = subprocess.Popen(
                command,
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