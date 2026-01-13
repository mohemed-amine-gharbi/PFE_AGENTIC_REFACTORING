# diagnostic_report.py
import json
import os

def generate_report(data, path="reports/diagnostic.json"):
    os.makedirs("reports", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
