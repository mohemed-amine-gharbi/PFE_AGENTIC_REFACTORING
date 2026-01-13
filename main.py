from core.orchestrator import Orchestrator
from diagnostics.report import DiagnosticReport

with open("examples/bad_code.py") as f:
    code = f.read()

orchestrator = Orchestrator()
results = orchestrator.run(code)

report = DiagnosticReport(results)
report.display()
