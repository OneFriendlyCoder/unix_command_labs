#!/usr/bin/env python3

import os
import sys
import subprocess
import filecmp
import json
import pwd

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import (
    load_ssh_private_key,
    load_ssh_public_key
)
from cryptography.hazmat.backends import default_backend

# Configuration: users, key names, and evaluation output
USERS = {
    'alice': os.path.expanduser('~alice'),
    'bob':   os.path.expanduser('~bob')
}
KEY_NAME = 'id_rsa'
EVALUATE_FILE = '/home/.evaluationScripts/evaluate.json'
SUBMISSIONS_FILE = '/home/labDirectory/submissions.txt'

# Helper: check file existence
def check_file_exists(path):
    return os.path.exists(path) and os.path.isfile(path)

# Helper: load key objects
def load_keys(priv_path, pub_path):
    try:
        priv_data = open(priv_path, 'rb').read()
        private_key = load_ssh_private_key(priv_data, password=None, backend=default_backend())
    except Exception:
        return None, None
    try:
        pub_data = open(pub_path, 'rb').read()
        public_key = load_ssh_public_key(pub_data, backend=default_backend())
    except Exception:
        return private_key, None
    return private_key, public_key

# Helper: compare private->public
def compare_keys(private_key, public_key):
    try:
        derived_bytes = private_key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
        orig_bytes = public_key.public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        )
    except Exception:
        return False
    return derived_bytes.split(b' ')[1] == orig_bytes.split(b' ')[1]

# Helper: extract command from submissions.txt
def get_submitted_command(keyword):
    try:
        with open(SUBMISSIONS_FILE, 'r') as f:
            for line in f:
                if line.startswith(keyword):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        return parts[1].strip()
    except Exception:
        return None
    return None

# Test cases implementation
def testcase_1():
    """
    1) Check that alice has both private and public keys generated,
       and that both files are owned by alice (not root or anyone else).
    """
    alice_home = USERS['alice']
    priv = os.path.join(alice_home, '.ssh', KEY_NAME)
    pub = priv + '.pub'
    if not (check_file_exists(priv) and check_file_exists(pub)):
        return False
    try:
        priv_owner = pwd.getpwuid(os.stat(priv).st_uid).pw_name
        pub_owner = pwd.getpwuid(os.stat(pub).st_uid).pw_name
    except Exception:
        return False
    return priv_owner == 'alice' and pub_owner == 'alice'


def testcase_2():
    """
    2) Verify passwordless SSH: key in bob's authorized_keys and successful SSH login.
       Also check that authorized_keys is owned by bob.
    """
    alice_home = USERS['alice']
    bob_home = USERS['bob']
    priv = os.path.join(alice_home, '.ssh', KEY_NAME)
    pub = priv + '.pub'
    auth_path = os.path.join(bob_home, '.ssh', 'authorized_keys')

    # load keys
    private_key, public_key = load_keys(priv, pub)
    if not private_key or not public_key:
        return False
    if not compare_keys(private_key, public_key):
        return False

    # authorized_keys check and ownership
    try:
        alice_key_part = open(pub, 'r').readline().split()[1]
        found = any(
            alice_key_part == line.split()[1]
            for line in open(auth_path)
            if len(line.split()) >= 2
        )
        auth_owner = pwd.getpwuid(os.stat(auth_path).st_uid).pw_name
    except Exception:
        return False

    if not found or auth_owner != 'bob':
        return False

    # login test
    try:
        result = subprocess.run([
            'su', '-', 'alice', '-c',
            'ssh -o PreferredAuthentications=publickey -o PasswordAuthentication=no bob@localhost echo SSH_SUCCESS'
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=5)
        return b'SSH_SUCCESS' in result.stdout
    except Exception:
        return False


def testcase_3():
    """
    3) Transfer single file shared.txt via student-submitted command.
       Run as alice, then check file exists in bob's home and owned by bob.
    """
    cmd = get_submitted_command('testcase 3')
    if not cmd:
        return False
    # execute command as alice
    try:
        result = subprocess.run(['su', '-', 'alice', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10)
        if result.returncode != 0:
            return False
    except Exception:
        return False

    bob_file = os.path.join(USERS['bob'], 'shared.txt')
    if not check_file_exists(bob_file):
        return False
    try:
        owner = pwd.getpwuid(os.stat(bob_file).st_uid).pw_name
    except Exception:
        return False
    return owner == 'bob'


def testcase_4():
    """
    4) Transfer directory 'big_folder' via student-submitted rsync command.
       Run as alice, then check directory and contents exist in bob's home and owned by bob.
    """
    cmd = get_submitted_command('testcase 4')
    if not cmd:
        return False
    try:
        result = subprocess.run(['su', '-', 'alice', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=20)
        if result.returncode != 0:
            return False
    except Exception:
        return False

    bob_dir = os.path.join(USERS['bob'], 'big_folder')
    if not os.path.isdir(bob_dir):
        return False
    # ownership check
    for root, dirs, files in os.walk(bob_dir):
        for name in dirs + files:
            path = os.path.join(root, name)
            try:
                owner = pwd.getpwuid(os.stat(path).st_uid).pw_name
                if owner != 'bob':
                    return False
            except Exception:
                return False
    return True

# Main execution: run tests, collect results
if __name__ == '__main__':
    tests = [testcase_1, testcase_2, testcase_3, testcase_4]
    dataSkel = []
    for i, test in enumerate(tests, start=1):
        passed = test()
        dataSkel.append({
            'testid': i,
            'status': 'success' if passed else 'fail',
            'score': 1 if passed else 0,
            'maximum marks': 1,
            'message': f"testcase {i} {'passed' if passed else 'failed'}"
        })

    os.makedirs(os.path.dirname(EVALUATE_FILE), exist_ok=True)
    with open(EVALUATE_FILE, 'w') as out:
        json.dump({'data': dataSkel}, out, indent=4)

    sys.exit(0 if all(d['status'] == 'success' for d in dataSkel) else 1)
