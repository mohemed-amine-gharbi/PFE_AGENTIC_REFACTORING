import openai
from dotenv import load_dotenv
import os

class LLMClient:
    def __init__(self, model_name="gpt-3.5-turbo"):
        load_dotenv()
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY non définie.")
        openai.api_key = self.api_key
        self.model_name = model_name

    def ask(self, system_prompt, user_prompt):
        """
        Version compatible OpenAI >=1.0.0
        """
        response = openai.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message['content']
