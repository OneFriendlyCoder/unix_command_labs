#!/usr/bin/env python3

import subprocess
import json
import os

# Configuration
SUBMISSION_FILE = "/home/labDirectory/submissions.txt"
EVALUATE_FILE   = "/home/.evaluationScripts/evaluate.json"

# Helper to run a shell command and capture its stdout (stripped)
def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        return ""

# 1) Load submitted answers (split on the last colon so "06:00" stays in the key)
submitted = {}
with open(SUBMISSION_FILE) as f:
    for line in f:
        if ':' not in line:
            continue
        key, val = line.rsplit(':', 1)
        submitted[key.strip().lower()] = val.strip()

# 2) Compute the correct values
correct = {
    "number of cronjobs for bob":
        run_cmd("crontab -u bob -l 2>/dev/null | grep -v '^$' | wc -l"),
    "number of cronjobs for alice":
        run_cmd("crontab -u alice -l 2>/dev/null | grep -v '^$' | wc -l"),
    "number of cronjobs for root":
        run_cmd("crontab -u root -l 2>/dev/null | grep -v '^$' | wc -l"),
    "name of the cronjob that runs every day at 06:00":
        run_cmd(
            "crontab -u root -l 2>/dev/null "
            "| grep -E '^0[[:space:]]+6[[:space:]]+\\*' "
            "| tail -n1 "
            "| sed -E 's/.*\\] (.+) executed.*/\\1/'"
        )
}

# 3) Build the skeleton of results
dataSkel = []
for i, (test_name, expected_ans) in enumerate(correct.items(), start=1):
    student_ans = submitted.get(test_name, "")
    passed = (student_ans == expected_ans)
    dataSkel.append({
        "testid": i,
        "status": "success" if passed else "fail",
        "score": 1 if passed else 0,
        "maximum marks": 1,
        "message": f"Test case {i} {'passed' if passed else 'failed'}"
    })

# 4) Write out evaluate.json
os.makedirs(os.path.dirname(EVALUATE_FILE), exist_ok=True)
with open(EVALUATE_FILE, 'w') as out:
    json.dump({"data": dataSkel}, out, indent=4)

# Exit non-zero if any failed
exit(0 if all(d["status"] == "success" for d in dataSkel) else 1)