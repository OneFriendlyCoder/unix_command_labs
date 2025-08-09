import os
import json
import pwd

BASE_DIR = "/home/labDirectory/"
EVALUATE_FILE = "/home/.evaluationScripts/evaluate.json"

tests = [
    {"testid": 1, "filename": "1.txt", "expected": "{T@sk1C0mpleteD}", "check_owner": True},
    {"testid": 2, "filename": "2.txt", "expected": "{T@sk2C0mpleteD}", "check_owner": False},
    {"testid": 3, "filename": "3.txt", "expected": "sh",               "check_owner": True},
]

results = []
for t in tests:
    results.append({
        "testid": t["testid"],
        "status": "fail",
        "score": 0,
        "maximum marks": 1,
        "message": f"Test case {t['testid']} failed"
    })

for idx, t in enumerate(tests):
    file_path = os.path.join(BASE_DIR, t["filename"])
    try:
        if not os.path.isfile(file_path):
            continue
        with open(file_path, 'r') as f:
            content = f.read().strip()
        if t.get("testid") == 3 and t.get("expected") == "sh":
            if content not in ("sh", "/bin/sh"):
                continue
        else:
            if content != t["expected"]:
                continue
        if t.get("check_owner"):
            stat_info = os.stat(file_path)
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
            if owner != "alice":
                continue

        results[idx].update({
            "status": "success",
            "score": 1,
            "message": f"Test case {t['testid']} success"
        })
    except:
        pass  

evaluate_data = {"data": results}
try:
    os.makedirs(os.path.dirname(EVALUATE_FILE), exist_ok=True)
    with open(EVALUATE_FILE, 'w') as eval_file:
        json.dump(evaluate_data, eval_file, indent=4)
except Exception as e:
    print(f"Failed to write evaluation file: {e}")
