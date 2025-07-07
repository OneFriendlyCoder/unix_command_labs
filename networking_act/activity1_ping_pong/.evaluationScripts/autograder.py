import subprocess
import re
import json

finaldata = {
    "data": []
}

def parse_solutions_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    command = None
    answers = {}

    for line in lines:
        if not command and re.match(r'^ping\s', line.strip()):
            command = line.strip()
        elif ':' in line:
            question, answer = map(str.strip, line.split(':', 1))
            answers[question] = answer if answer else "<Not Answered>"

    return command, answers

def run_command_and_check_ping(command):
    try:
        # Ensure exactly 5 pings are sent
        if not re.search(r'\s-c\s+5\b', command):
            return 0

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout
            match = re.search(r'(\d+) packets transmitted, (\d+) received, (\d+)% packet loss', output)
            if match:
                packets_transmitted = int(match.group(1))
                packets_received = int(match.group(2))
                packet_loss = int(match.group(3))
                if packets_transmitted == packets_received and packet_loss == 0:
                    return 1
    except Exception:
        return 0
    return 0

def main():
    solutions_file = '/home/labDirectory/solutions.txt'
    command, answers = parse_solutions_file(solutions_file)

    # Test case 1: Check if exactly 5 pings were sent and all succeeded
    dataSkel = {
        "testid": 1,
        "status": "fail",
        "score": 0,
        "maximum marks": 1,
        "message": "Test case 1 failed"
    }

    if command and run_command_and_check_ping(command):
        dataSkel["status"] = "pass"
        dataSkel["score"] = 1
        dataSkel["message"] = "Test case 1 passed"
    
    finaldata["data"].append(dataSkel)

    # Test case 2: Check flag for number of packets
    dataSkel = {
        "testid": 2,
        "status": "fail",
        "score": 0,
        "maximum marks": 1,
        "message": "Test case 2 failed"
    }

    if answers.get("Which flag specifies the number of packets to send before stopping?") == "-c":
        dataSkel["status"] = "pass"
        dataSkel["score"] = 1
        dataSkel["message"] = "Test case 2 passed"

    finaldata["data"].append(dataSkel)

    # Test case 3: Check flag for interval adjustment
    dataSkel = {
        "testid": 3,
        "status": "fail",
        "score": 0,
        "maximum marks": 1,
        "message": "Test case 3 failed"
    }

    if answers.get("Which flag can be used to change the interval between consecutive ping requests?") == "-i":
        dataSkel["status"] = "pass"
        dataSkel["score"] = 1
        dataSkel["message"] = "Test case 3 passed"

    finaldata["data"].append(dataSkel)

    # Save results
    with open('/home/.evaluationScripts/evaluate.json', 'w', encoding='utf-8') as f:
        json.dump(finaldata, f, indent=4)

if __name__ == "__main__":
    main()
