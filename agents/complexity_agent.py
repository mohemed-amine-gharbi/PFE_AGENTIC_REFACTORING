from agents.base_agent import BaseAgent


class ComplexityAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="ComplexityAgent")

    # def build_prompt(self, code, language):
    #     return (
    #         f"Analyse ce code {language} et propose un refactoring pour réduire la complexité algorithmique. "
    #         "Si possible, transforme les boucles imbriquées ou opérations coûteuses pour améliorer l'efficacité. "
    #         "Retourne uniquement le code refactoré."
    #     )

    def build_prompt(self, code, language):
        return f"""You are an autonomous AI code-refactoring agent specialized in Python. Given Python source code, detect complexity-related code smells and refactor the code to reduce complexity while preserving identical semantics.

### Complexity Smells to Detect
- High cyclomatic or cognitive complexity
- Deep or unnecessary nesting
- Overly long functions or methods
- Mixed responsibilities within a single unit
- Complex or duplicated conditional and boolean logic
- Repeated control-flow patterns
- Implicit or hidden control flow

### Semantic Preservation Constraints (Mandatory)
- Preserve exact behavior for all inputs and edge cases
- Do not change return values, side effects, raised exceptions, or execution order
- Preserve short-circuit logic, mutation timing, and evaluation order
- Do not change public APIs or function signatures
- Preserve logging, I/O, randomness, time usage, and global or shared state
- If a refactor risks semantic change, do not apply it

### Required Output
1. Detected complexity code smells with location and brief rationale
2. Fully refactored Python code in a single code block
3. Short justification explaining why semantics are unchanged
"""

    def analyze(self, code, language):
        # Analyse simplifiée: détecte les boucles imbriquées
        nested_loops = [line for line in code.splitlines() if "for" in line or "while" in line]
        return nested_loops

    def apply(self, code, language, temperature=None):
        return super().apply(code, language, temperature)



























































































"""from agents.base_agent import BaseAgent

class ComplexityAgent(BaseAgent):
    def __init__(self, llm):
        self.llm = llm
        self.name = "ComplexityAgent"

    # def build_prompt(self, code, language):
    #     return (
    #         f"Analyse ce code {language} et propose un refactoring pour réduire la complexité algorithmique. "
    #         "Si possible, transforme les boucles imbriquées ou opérations coûteuses pour améliorer l'efficacité. "
    #         "Retourne uniquement le code refactoré."
    #     )
    def build_prompt(self, code, language):
     return f""""""You are an autonomous AI code-refactoring agent specialized in Python. Given Python source code, detect complexity-related code smells and refactor the code to reduce complexity while preserving identical semantics.

            ### Complexity Smells to Detect
            - High cyclomatic or cognitive complexity
            - Deep or unnecessary nesting
            - Overly long functions or methods
            - Mixed responsibilities within a single unit
            - Complex or duplicated conditional and boolean logic
            - Repeated control-flow patterns
            - Implicit or hidden control flow

            ### Semantic Preservation Constraints (Mandatory)
            - Preserve exact behavior for all inputs and edge cases
            - Do not change return values, side effects, raised exceptions, or execution order
            - Preserve short-circuit logic, mutation timing, and evaluation order
            - Do not change public APIs or function signatures
            - Preserve logging, I/O, randomness, time usage, and global or shared state
            - If a refactor risks semantic change, do not apply it

            ### Required Output
            1. Detected complexity code smells with location and brief rationale
            2. Fully refactored Python code in a single code block
            3. Short justification explaining why semantics are unchanged"""
"""


   def analyze(self, code):
        # Analyse simplifiée: détecte les boucles imbriquées
        nested_loops = [line for line in code.splitlines() if "for" in line or "while" in line]
        return nested_loops
    def apply(self, code, language, temperature=None):
        analysis = self.analyze(code)
        if analysis:
            prompt = self.build_prompt(code, language)
            if temperature is not None:
                proposal = self.llm.ask(
                    system_prompt=prompt,
                    user_prompt=code,
                    temperature=temperature
                )
            else:
                proposal = self.llm.ask(system_prompt=prompt, user_prompt=code)
        else:
            proposal = code
        return {
            "name": self.name, 
            "analysis": analysis, 
            "proposal": proposal,
            "temperature_used": temperature
        }"""