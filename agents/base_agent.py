class BaseAgent:
    def __init__(self, name, llm_client):
        self.name = name
        self.llm = llm_client

    def analyze(self, code: str):
        raise NotImplementedError

    def build_prompt(self, analysis, code):
        raise NotImplementedError

    def reason_with_llm(self, analysis, code):
        prompt = self.build_prompt(analysis, code)
        return self.llm.ask(
            system_prompt=f"You are a refactoring agent specialized in {self.name}.",
            user_prompt=prompt
        )
