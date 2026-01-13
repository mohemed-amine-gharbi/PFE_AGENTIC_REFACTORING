# main.py
from orchestrator import Orchestrator
from diagnostic_report import generate_report

with open("sample_code/bad_code.py", encoding="utf-8") as f:
    code = f.read()

orch = Orchestrator()
report = orch.run(code)

generate_report(report)

print("✅ Analyse terminée. Rapport généré dans reports/diagnostic.json")
