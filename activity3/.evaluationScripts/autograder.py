#!/usr/bin/env python3

import os
import pwd
import grp
import json

# === Configuration ===
EVALUATE_FILE = "/home/.evaluationScripts/evaluate.json"
readme_path = "/home/labDirectory/chown_lab/README.md"
file1_path = "/home/labDirectory/chown_lab/src/module1/file1.txt"
src_dir = "/home/labDirectory/chown_lab/src"

# === Helper ===
def get_owner_group(path):
    stat_info = os.stat(path)
    uid = stat_info.st_uid
    gid = stat_info.st_gid
    owner = pwd.getpwuid(uid).pw_name
    group = grp.getgrgid(gid).gr_name
    return owner, group

# === Initialize result skeleton ===
results = []
for i in range(1, 4):
    results.append({
        "testid": i,
        "status": "fail",
        "score": 0,
        "maximum marks": 1,
        "message": f"Test case {i} failed"
    })

# === Test Case 1: README.md owned by alice ===
if os.path.exists(readme_path):
    owner, _ = get_owner_group(readme_path)
    if owner == "alice":
        results[0].update({
            "status": "success",
            "score": 1,
            "message": "Test case 1 passed"
        })

# === Test Case 2: file1.txt owned by alice and group projectgroup ===
if os.path.exists(file1_path):
    owner, group = get_owner_group(file1_path)
    if owner == "alice" and group == "projectgroup":
        results[1].update({
            "status": "success",
            "score": 1,
            "message": "Test case 2 passed"
        })

# === Test Case 3: All under src/ owned by alice ===
def all_owned_by_alice(path):
    for root, dirs, files in os.walk(path):
        for name in dirs + files:
            full_path = os.path.join(root, name)
            try:
                owner, _ = get_owner_group(full_path)
                if owner != "alice":
                    return False
            except:
                return False
    return True

if os.path.exists(src_dir) and all_owned_by_alice(src_dir):
    results[2].update({
        "status": "success",
        "score": 1,
        "message": "Test case 3 passed"
    })

# === Write to JSON file ===
os.makedirs(os.path.dirname(EVALUATE_FILE), exist_ok=True)
with open(EVALUATE_FILE, 'w') as f:
    json.dump({"data": results}, f, indent=4)