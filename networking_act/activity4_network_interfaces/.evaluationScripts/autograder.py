import subprocess
import re
import copy
import json
import os
import difflib
import shutil

finaldata = {
    "data": []
}

dataSkel = {
    "testid": 1,
    "status": "fail",
    "score": 0,
    "maximum marks": 1,
    "message": "Autograder Failed !"
}

def parse_solutions_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    command = None
    answers = {}

    for line in lines:
        # Look for a command starting with "ip" (as required for activity 4)
        stripped_line = line.strip()
        if not command and re.match(r'^ip\s', stripped_line):
            command = stripped_line
        elif ':' in stripped_line:
            question, answer = map(str.strip, stripped_line.split(':', 1))
            answers[question] = answer if answer else "<Not Answered>"
    return command, answers

def run_command(command):
    try:
        # Validate that the user provided a nonempty command starting with "ip"
        if not command or not command.startswith("ip "):
            return 0

        # Define file paths:
        autograder_file = "/home/.evaluationScripts/ipv4_addresses.txt"
        student_manual_file = "/home/labDirectory/ipv4_addresses.txt"
        correct_file = "/home/.evaluationScripts/correct_ipv4_addresses.txt"

        # Remove the autograder file if it exists to force a fresh generation.
        if os.path.exists(autograder_file):
            os.remove(autograder_file)

        # Change directory to evaluationScripts so that the command runs there.
        eval_path = "/home/.evaluationScripts/"
        os.chdir(eval_path)

        # Execute the student's command.
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return 0

        # If the autograder file was not created by the command, try to "download"
        # it by copying the manually generated file from the labDirectory.
        if not os.path.isfile(autograder_file):
            if os.path.isfile(student_manual_file):
                shutil.copy(student_manual_file, autograder_file)
            else:
                return 0

        # Check that the student manual file exists.
        if not os.path.isfile(student_manual_file):
            return 0

        # Check that the correct answer file exists.
        if not os.path.isfile(correct_file):
            return 0

        # Compare the autograder-generated file with the correct file.
        with open(autograder_file, 'r') as f1, open(correct_file, 'r') as f2:
            autograder_lines = f1.readlines()
            correct_lines = f2.readlines()
        diff_autograder = ''.join(difflib.unified_diff(autograder_lines, correct_lines,
                                                         fromfile=autograder_file,
                                                         tofile=correct_file))

        # Compare the manually generated file with the correct file.
        with open(student_manual_file, 'r') as f1, open(correct_file, 'r') as f2:
            student_lines = f1.readlines()
            correct_lines = f2.readlines()
        diff_student = ''.join(difflib.unified_diff(student_lines, correct_lines,
                                                    fromfile=student_manual_file,
                                                    tofile=correct_file))

        # If differences are found in either comparison, the test fails.
        if diff_autograder or diff_student:
            return 0
        else:
            return 1

    except Exception as e:
        # Optionally log the exception e if needed.
        return 0

def main():
    solutions_file = '/home/labDirectory/solutions.txt'
    command, answers = parse_solutions_file(solutions_file)

    # Test case 1: Verify that a valid command was provided and that executing it
    # produces an output (or downloads a copy) matching the correct file.
    if command and run_command(command):
        dataSkel["testid"] = 1
        dataSkel["status"] = "success"
        dataSkel["score"] = 1
        dataSkel["message"] = "Test case 1 passed"
    else:
        dataSkel["testid"] = 1
        dataSkel["status"] = "fail"
        dataSkel["score"] = 0
        dataSkel["message"] = "Test case 1 failed"
    finaldata["data"].append(copy.deepcopy(dataSkel))

    with open('/home/.evaluationScripts/evaluate.json', 'w', encoding='utf-8') as f:
        json.dump(finaldata, f, indent=4)

if __name__ == "__main__":
    main()
