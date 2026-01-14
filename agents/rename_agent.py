class RenameAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, code):
        bad_names = []
        if "def f(" in code:
            bad_names.append("f")
        for v in [" a,", " b,", " c,"]:
            if v in code:
                bad_names.append(v.strip())
        return bad_names

    def prompt(self, analysis, code):
        if not analysis:
            return code

        return f"""
You are a Python refactoring agent.

Rename poorly named identifiers:
- f → process_values
- a → threshold
- b → limit
- c → count

Return ONLY the refactored Python code.
Do NOT explain anything.

CODE:
{code}
"""
