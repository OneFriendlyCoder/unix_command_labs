import subprocess
import re
import copy
import json
import os
import hashlib

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
        if not command and re.match(r'^wget\s', line.strip()):
            command = line.strip()
        elif ':' in line:
            question, answer = map(str.strip, line.split(':', 1))
            answers[question] = answer if answer else "<Not Answered>"

    return command, answers

def run_command(command):
    """
    Returns:
        Success:
            0: Both the file present and file which gets downloaded by student's command are the same
        Failures:
            1: No downloads directory created by student command - test case failed.
            2: No "system_update" file present in student's download directory
            3: Some error in executing student's command 
            4: The file present in student's download directory and the file which gets downloaded are not the same - test case failed
    """
    try:
        script_dir = "/home/.evaluationScripts/"
        
        # check if the file is present inside downloads directory:
        files_and_dirs = os.listdir(script_dir)
        download_dir = None
        for item in files_and_dirs:
            if item.lower() == 'downloads':
                download_dir = item
                break
        
        if not download_dir:
            return 1 # this will represent that the student did not use "-P" (or "--directory-prefix")

        # Define file paths
        existing_file_path = os.path.join(script_dir, download_dir, "system_update")
        
        if not os.path.isfile(existing_file_path):
            return 2 # this represents that file was not downloaded, student just created downloads dir
        else:
            existing_file_hash = hashlib.sha256()
            with open(existing_file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    existing_file_hash.update(byte_block)
            existing_file_hash.hexdigest()
            
        
        # Run the wget command in /tmp directory
        os.chdir("/tmp")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return 3 # this represents some error in executing student's command

        # Check if both files exist after running the command
        downloaded_file_path = os.path.join("/tmp", download_dir, "system_update")
        downloaded_file_hash = None
        
        if os.path.isfile(existing_file_path):
            try:
                downloaded_file_hash = hashlib.sha256()
                with open(downloaded_file_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        downloaded_file_hash.update(byte_block)
                downloaded_file_hash.hexdigest()
                os.chdir(script_dir) # restore the working directory for other test cases.
                if downloaded_file_hash == existing_file_hash:
                    return 0  # Success
                else:
                    return 4  # Files are not the same

            except FileNotFoundError:
                return 0
        else:
            return 0
    except Exception as e:
        return 0

def main():
    solutions_file = '/home/labDirectory/solutions.txt'
    command, answers = parse_solutions_file(solutions_file)

    # Test case 1
    return_code_run_command = run_command(command) == 0
    if command and return_code_run_command == 0:
        dataSkel["testid"] = 1
        dataSkel["status"] = "pass"
        dataSkel["score"] = 1
        dataSkel["message"] = "Test case 1 passed"
    else:
        dataSkel["testid"] = 1
        dataSkel["status"] = "fail"
        dataSkel["score"] = 0
        if return_code_run_command == 1:
            dataSkel["message"] = "Test case 1 failed\n The command did not create download directory!" 
        if return_code_run_command == 2:
            dataSkel["message"] = "Test case 1 failed\n No system_update file in download directory!" 
        if return_code_run_command == 3:
            dataSkel["message"] = "Test case 1 failed\n There's some error in your command!" 
        if return_code_run_command == 4:
            dataSkel["message"] = "Test case 1 failed\n Tampered the downloaded file!" 
           
    finaldata["data"].append(copy.deepcopy(dataSkel))  # Add test case 1 result

    # Test case 2
    if answers:
        if "P" or "directory-prefix" in answers.get("Which flag allows to specify the directory where the downloaded file will be saved?"):
            dataSkel["testid"] = 2
            dataSkel["status"] = "pass"
            dataSkel["score"] = 1
            dataSkel["message"] = "Test case 2 passed"
        else:
            dataSkel["testid"] = 2
            dataSkel["status"] = "fail"
            dataSkel["score"] = 0
            dataSkel["message"] = "Test case 2 failed"            
        finaldata["data"].append(copy.deepcopy(dataSkel))  # Add test case 2 result

        # Test case 3
        if "limit-rate" in answers.get("Which flag can be used to limit the download speed?"):
            dataSkel["testid"] = 3
            dataSkel["status"] = "pass"
            dataSkel["score"] = 1
            dataSkel["message"] = "Test case 3 passed"
        else:
            dataSkel["testid"] = 3
            dataSkel["status"] = "fail"
            dataSkel["score"] = 0
            dataSkel["message"] = "Test case 3 failed"     
        finaldata["data"].append(copy.deepcopy(dataSkel))  # Add test case 3 result

    with open('/home/.evaluationScripts/evaluate.json', 'w', encoding='utf-8') as f:
        json.dump(finaldata, f, indent=4)

if __name__ == "__main__":
    main()