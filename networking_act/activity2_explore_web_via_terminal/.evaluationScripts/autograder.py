import subprocess
import re
import copy
import json
import os
import difflib

finaldata = {
    "data" : []
}

dataSkel = {
    "testid" : 1,
    "status" : "fail",
    "score" : 0,
    "maximum marks" : 1,
    "message" : "Autograder Failed !"
}

def parse_solutions_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    command = None
    answers = {}

    for line in lines:
        if not command and re.match(r'^curl\s', line.strip()):
            command = line.strip()
        elif ':' in line:
            question, answer = map(str.strip, line.split(':', 1))
            answers[question] = answer if answer else "<Not Answered>"

    return command, answers

def run_command(command):
    try:
        script_dir = "/home/.evaluationScripts/"
        os.chdir(script_dir)
        
        # Remove the file to ensure fresh generation by the command
        file_path1 = os.path.join(script_dir, "activity2.html")
        if os.path.exists(file_path1):
            os.remove(file_path1)
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            # If the curl command failed, return 0 immediately
            return 0

        file_path2 = os.path.join(script_dir, "index.html")
        
        # Ensure both files exist after running the command
        if os.path.isfile(file_path1) and os.path.isfile(file_path2):
            try:
                with open(file_path1, 'r') as f1, open(file_path2, 'r') as f2:
                    f1lines = f1.readlines()
                    f2lines = f2.readlines()
                
                diff = difflib.unified_diff(f1lines, f2lines, fromfile=file_path1, tofile=file_path2)
                diff_output = ''.join(diff)
                if diff_output:
                    return 0  # Files differ: test case fails
                else:
                    return 1  # Files are identical: test case passes

            except FileNotFoundError:
                return 0
        else:
            return 0
    except Exception:
        return 0


def main():
    solutions_file = '/home/labDirectory/solutions.txt'
    command, answers = parse_solutions_file(solutions_file)

    # Test case 1
    if command and run_command(command):
        dataSkel["testid"] = 1
        dataSkel["status"] = "pass"
        dataSkel["score"] = 1
        dataSkel["message"] = f"Test case 1 passed"
    else:
        dataSkel["testid"] = 1
        dataSkel["status"] = "fail"
        dataSkel["score"] = 0
        dataSkel["message"] = f"Test case 1 failed"            
    finaldata["data"].append(copy.deepcopy(dataSkel))  # Add test case 1 result

    # Test case 2
    if answers:
        if answers["Which flag allows you to specify the output file name?"] == "-o":
            dataSkel["testid"] = 2
            dataSkel["status"] = "pass"
            dataSkel["score"] = 1
            dataSkel["message"] = f"Test case 2 passed"
        else:
            dataSkel["testid"] = 2
            dataSkel["status"] = "fail"
            dataSkel["score"] = 0
            dataSkel["message"] = f"Test case 2 failed"            
        finaldata["data"].append(copy.deepcopy(dataSkel))  # Add test case 2 result

        # Test case 3
        if answers["Which flag is used to follow redirects?"] == "-L":
            dataSkel["testid"] = 3
            dataSkel["status"] = "pass"
            dataSkel["score"] = 1
            dataSkel["message"] = f"Test case 3 passed"
        else:
            dataSkel["testid"] = 3
            dataSkel["status"] = "fail"
            dataSkel["score"] = 0
            dataSkel["message"] = f"Test case 3 failed"     
        finaldata["data"].append(copy.deepcopy(dataSkel))  # Add test case 3 result

    with open('/home/.evaluationScripts/evaluate.json', 'w', encoding='utf-8') as f:
        json.dump(finaldata, f, indent=4)

if __name__ == "__main__":
    main()
