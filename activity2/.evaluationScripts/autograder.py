import os
import json
import pwd

# Configuration
BASE_DIR = "/home/labDirectory/"
EVALUATE_FILE = "/home/.evaluationScripts/evaluate.json"

# Test definitions: filename, expected content, require alice ownership
tests = [
    {"testid": 1, "filename": "1.txt", "expected": "{T@sk1C0mpleteD}", "check_owner": True},
    {"testid": 2, "filename": "2.txt", "expected": "{T@sk2C0mpleteD}", "check_owner": False},  # Ownership check disabled
    {"testid": 3, "filename": "3.txt", "expected": "sh",               "check_owner": True},
    # Removed testid 4
]

# Initialize results
results = []
for t in tests:
    results.append({
        "testid": t["testid"],
        "status": "fail",
        "score": 0,
        "maximum marks": 1,
        "message": f"Test case {t['testid']} failed"
    })

# Evaluate each test
for idx, t in enumerate(tests):
    file_path = os.path.join(BASE_DIR, t["filename"])
    try:
        # Check existence
        if not os.path.isfile(file_path):
            continue
        # Read content
        with open(file_path, 'r') as f:
            content = f.read().strip()
        if content != t["expected"]:
            continue
        # Check owner if required
        if t.get("check_owner"):
            stat_info = os.stat(file_path)
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            if owner != "alice":
                continue
        # All checks passed
        results[idx].update({
            "status": "pass",
            "score": 1,
            "message": f"Test case {t['testid']} passed"
        })
    except:
        pass  # Fail silently, leave default fail message

# Write evaluation results
evaluate_data = {"data": results}
try:
    os.makedirs(os.path.dirname(EVALUATE_FILE), exist_ok=True)
    with open(EVALUATE_FILE, 'w') as eval_file:
        json.dump(evaluate_data, eval_file, indent=4)
except Exception as e:
    print(f"Failed to write evaluation file: {e}")
