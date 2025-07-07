#!/usr/bin/env bash
set -euo pipefail

# Check for root
if [[ "$EUID" -ne 0 ]]; then
  echo "Error: This script must be run as root." >&2
  exit 1
fi

# check if rsync is installed if not then install
if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync not found. Installing..."
  apt-get update
  apt-get install -y rsync
  # echo "rsync has been installed."
else
  echo "rsync is already installed. Nothing to do."
fi

# Ensure OpenSSH client & server are installed
if ! dpkg -s openssh-client >/dev/null 2>&1 || ! dpkg -s openssh-server >/dev/null 2>&1; then
  apt-get update
  apt-get install -y openssh-client openssh-server
fi

# Start the SSH service
service ssh start

# Define users and passwords
declare -A USERS=(
  [alice]="alice@123"
  [bob]="bob@123"
)

for user in "${!USERS[@]}"; do
  pass="${USERS[$user]}"

  if id "$user" &>/dev/null; then
    echo "User '$user' already exists, skipping creation."
  else
    useradd -m -d "/home/$user" -s "/bin/bash" "$user"
    echo "Created user '$user' with home /home/$user."

    # If this is alice, create shared.txt and a large folder structure
    if [[ "$user" == "alice" ]]; then
      # Create a shared text file with paragraph content
      cat << 'EOF' > /home/alice/shared.txt
This is a sample shared file. It contains a paragraph of text to demonstrate file creation within the script. Feel free to modify or extend this content as needed for your use case.
EOF
      echo "Created /home/alice/shared.txt."

      # Create a large folder with subfolders and files up to ~0.5 GB total
      base_dir="/home/alice/big_folder"
      mkdir -p "$base_dir"
      # Generate 5 subdirectories, each with a 100MB file
      for i in {1..5}; do
        subdir="$base_dir/dir$i"
        mkdir -p "$subdir"
        # Create a 100MB file using dd
        dd if=/dev/urandom of="$subdir/file$i.bin" bs=1M count=100 status=none
      done
      echo "Created large folder structure under /home/alice/big_folder (~500MB)."

      # Ensure correct ownership of new files and folders
      chown -R alice:alice "/home/alice/shared.txt" "$base_dir"

      # Fix permissions on .ssh directory
      ssh_dir="/home/alice/.ssh"
      mkdir -p "$ssh_dir"
      chown -R alice:alice "$ssh_dir"
      chmod 700 "$ssh_dir"
    fi
  fi

  # Set the password non-interactively
  echo "$user:$pass" | chpasswd
  echo "Password for '$user' set."

  # Ensure correct ownership on home directory
  chown -R "$user":"$user" "/home/$user"
done

exec mongod \
  --bind_ip_all \
  --dbpath /data/db \
  --logpath /var/log/mongodb/mongod.log \
  --logappend
