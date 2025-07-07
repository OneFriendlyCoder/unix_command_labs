#!/usr/bin/env bash

# CHOWN Labs: Project Access Control Simulation - Activity 3
# Simulates access control for project "Chronos".
# Single developer: alice; root owns modules initially.

# Ensure the script is run as root
if [[ $EUID -ne 0 ]]; then
  echo "Must be run as root."
  exit 1
fi

# 1) Create user alice if it doesn't exist and set password
id alice &>/dev/null || useradd -m -s /bin/bash alice && echo "alice:alice@123" | chpasswd

# 2) Create project group and add root (simulates using root as second developer)
getent group projectgroup >/dev/null || groupadd projectgroup
usermod -aG projectgroup root

# 3) Add alice to sudo group (Debian/Ubuntu standard)
getent group sudo >/dev/null || groupadd sudo
usermod -aG sudo alice

# 4) Prepare alice's home directory
ALICE_HOME="/home/alice"
if [ ! -d "$ALICE_HOME" ]; then
  mkdir -p "$ALICE_HOME"
  chown alice:alice "$ALICE_HOME"
  chmod 700 "$ALICE_HOME"
fi

# Ensure alice's shell startup sets her to home directory
BASHRC="$ALICE_HOME/.bashrc"
grep -qxF 'cd ~' "$BASHRC" || echo 'cd ~' >> "$BASHRC"
chown alice:alice "$BASHRC"

# 5) Build project directory tree under alice (owned by root:projectgroup)
LAB_DIR="/home/labDirectory/chown_lab"
mkdir -p "$LAB_DIR/src/module1" "$LAB_DIR/src/module2"

# 6) Create files in the lab tree
touch "$LAB_DIR/README.md"
touch "$LAB_DIR/src/module1/file1.txt" "$LAB_DIR/src/module1/file2.log"
touch "$LAB_DIR/src/module2/file3.txt"

# 7) Set initial ownership to root:projectgroup and restrictive permissions
chown -R root:projectgroup "$LAB_DIR"
chmod -R 700 "$LAB_DIR/src"
chmod 600 "$LAB_DIR/README.md"

exec mongod \
  --bind_ip_all \
  --dbpath /data/db \
  --logpath /var/log/mongodb/mongod.log \
  --logappend