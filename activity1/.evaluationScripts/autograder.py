import subprocess
import json
import time
import os

# Configuration
SUBMISSION_FILE = "/home/labDirectory/submissions.txt"
EVALUATE_FILE   = "/home/.evaluationScripts/evaluate.json"

# Define the correct commands
correct_cmds = [
    "ss -t",
    "ss -t -n",
    "ss -u",
    "ss -u -n",
    "ss -t -l",
    "ss -u -l",
]

def run_command(cmd):
    try:
        parts = cmd.strip().split()
        return subprocess.check_output(parts, stderr=subprocess.STDOUT, text=True).strip()
    except subprocess.CalledProcessError as e:
        return e.output.strip()
    except Exception as exc:
        return f"ERROR: {exc}"

def main():
    # Read student submissions
    if not os.path.exists(SUBMISSION_FILE):
        print(f"Submission file not found: {SUBMISSION_FILE}")
        return

    with open(SUBMISSION_FILE, 'r') as f:
        student_cmds = [line.strip() for line in f if line.strip()]

    # Warn if count mismatch
    # if len(student_cmds) != len(correct_cmds):
    #     print(f"Expected {len(correct_cmds)} commands, found {len(student_cmds)} in {SUBMISSION_FILE}")

    # Pre‐run all correct cmds once
    correct_outputs = [run_command(c) for c in correct_cmds]

    # Build results in one pass
    results = []
    for idx, (correct_out, expected_cmd) in enumerate(zip(correct_outputs, correct_cmds), start=1):
        if idx <= len(student_cmds):
            student_out = run_command(student_cmds[idx-1])
            passed = (student_out == correct_out)
            results.append({
                "testid": idx,
                "status": "success" if passed else "fail",
                "score": 1 if passed else 0,
                "maximum marks": 1,
                "message": f"Test case {idx} {'passed' if passed else 'failed'}"
            })
        else:
            # missing submission
            results.append({
                "testid": idx,
                "status": "fail",
                "score": 0,
                "maximum marks": 1,
                "message": f"Test case {idx} failed: no submission provided"
            })

    # Write out
    os.makedirs(os.path.dirname(EVALUATE_FILE), exist_ok=True)
    with open(EVALUATE_FILE, 'w') as out:
        json.dump({"data": results}, out, indent=4)

if __name__ == "__main__":
    main()
