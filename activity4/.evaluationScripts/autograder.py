#!/usr/bin/env python3

import subprocess
import json
import os

# Configuration for output file
EVALUATE_FILE = "/home/.evaluationScripts/evaluate.json"

# Helper to run a shell command and return True if exit code is zero
def is_installed(cmd):
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

# Prepare data skeleton: 2 test cases (git, htop)
dataSkel_list = [
    {"testid": 1, "status": "fail", "score": 0, "maximum marks": 1, "message": "vim installation check failed"},
    {"testid": 2, "status": "fail", "score": 0, "maximum marks": 1, "message": "htop installation check failed"}
]

# --- Check git installation ---
if is_installed("vim --version"):
    dataSkel_list[0]["status"] = "success"
    dataSkel_list[0]["score"] = 1
    dataSkel_list[0]["message"] = "vim is installed"
else:
    dataSkel_list[0]["message"] = "vim is not installed"

# --- Check htop installation ---
if is_installed("htop --version"):
    dataSkel_list[1]["status"] = "success"
    dataSkel_list[1]["score"] = 1
    dataSkel_list[1]["message"] = "htop is installed"
else:
    dataSkel_list[1]["message"] = "htop is not installed"

# Write results to evaluate.json
os.makedirs(os.path.dirname(EVALUATE_FILE), exist_ok=True)
with open(EVALUATE_FILE, 'w') as eval_file:
    json.dump({"data": dataSkel_list}, eval_file, indent=4)
