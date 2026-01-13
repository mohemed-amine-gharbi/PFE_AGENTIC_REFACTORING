class BaseAgent:
    def __init__(self, name, llm_client):
        self.name = name
        self.llm = llm_client

    def analyze(self, code):
        raise NotImplementedError

    def reason_with_llm(self, analysis):
        prompt = self.build_prompt(analysis)
        return self.llm.ask(
            system_prompt=f"You are a refactoring agent specialized in {self.name}",
            user_prompt=prompt
        )

    def build_prompt(self, analysis):
        raise NotImplementedError
