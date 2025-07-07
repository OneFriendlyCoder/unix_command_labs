#!/usr/bin/env bash
set -e

# 0) Fix labDirectory perms
chmod 777 /home/labDirectory

# 1) Create 'alice' and set password
if ! id alice &>/dev/null; then
  useradd -m -s /bin/bash alice
  echo "alice:alice123" | chpasswd
  echo "Created user 'alice' with password alice123."
else
  echo "User 'alice' already exists."
fi

# 2) Configure alice’s bash_profile
ALICE_PROFILE="/home/alice/.bash_profile"
touch "$ALICE_PROFILE"
chown alice:alice "$ALICE_PROFILE"
if ! grep -qxF 'export LABVAR={T@sk2C0mpleteD}' "$ALICE_PROFILE"; then
  echo 'export LABVAR={T@sk2C0mpleteD}' >> "$ALICE_PROFILE"
  echo "Added LABVAR to $ALICE_PROFILE"
else
  echo "LABVAR already in $ALICE_PROFILE"
fi

# 3) Configure root’s bash_profile and export in this shell
ROOT_PROFILE="/root/.bash_profile"
touch "$ROOT_PROFILE"
if ! grep -qxF 'export EXPORT_ME={T@sk4C0mpleteD}' "$ROOT_PROFILE"; then
  echo 'export EXPORT_ME={T@sk4C0mpleteD}' >> "$ROOT_PROFILE"
  echo "Added EXPORT_ME to $ROOT_PROFILE"
  export EXPORT_ME={T@sk4C0mpleteD}
  echo "Exported EXPORT_ME in the entrypoint environment"
else
  echo "EXPORT_ME already in $ROOT_PROFILE"
fi

# 4) Prevent alice from inheriting EXPORT_ME
if ! grep -qxF 'unset EXPORT_ME' "$ALICE_PROFILE"; then
  echo 'unset EXPORT_ME' >> "$ALICE_PROFILE"
  chown alice:alice "$ALICE_PROFILE"
  echo "Added unset EXPORT_ME to $ALICE_PROFILE"
else
  echo "unset EXPORT_ME already in $ALICE_PROFILE"
fi

# 5) Finally exec mongod as PID 1 (no duplicate runs!)
exec mongod \
  --bind_ip_all \
  --dbpath /data/db \
  --logpath /var/log/mongodb/mongod.log \
  --logappend
