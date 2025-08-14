#!/usr/bin/env bash
set -euo pipefail

# Target directory
DEST_DIR="/home/labDirectory/"
DEB_URL="http://ftp.de.debian.org/debian/pool/main/h/htop/htop_3.4.1-5_amd64.deb"
DEB_NAME="$(basename "$DEB_URL")"

# Ensure running as root
if [[ "$EUID" -ne 0 ]]; then
  echo "Please run as root or with sudo." >&2
  exit 1
fi

# Suppress interactive prompts
export DEBIAN_FRONTEND=noninteractive
APT_OPTS=("-y" "-qq")
DPKG_OPTS=("--force-confdef" "--force-confold")

# Update package index quietly
echo "Updating package index..."
apt-get update -qq

# Installing the proper version of git
# apt install git=1:2.43.0-1ubuntu7.2

# Repair any broken dependencies quietly
apt-get install "${APT_OPTS[@]}" -f >/dev/null 2>&1 || true
apt-get install -y libnl-3-200 libnl-genl-3-200

# Uninstall htop and vim if present, without installing them later
# echo "Removing existing htop and vim..."
apt-get purge "${APT_OPTS[@]}" htop vim >/dev/null 2>&1 || true

# Create target directory if missing
# echo "Preparing destination: $DEST_DIR"
mkdir -p "$DEST_DIR"
cd /var/tmp
apt-get download htop
mv htop_*.deb /home/labDirectory/
cd "$DEST_DIR"

# Download the specified git .deb file into destination
# echo "Downloading $DEB_NAME to $DEST_DIR"
# curl -sSL "$DEB_URL" -o "$DEST_DIR/$DEB_NAME"

exec mongod \
  --bind_ip_all \
  --dbpath /data/db \
  --logpath /var/log/mongodb/mongod.log \
  --logappend
