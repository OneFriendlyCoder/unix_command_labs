#!/usr/bin/env bash
set -euo pipefail

# Ensure running as root
if (( EUID != 0 )); then
  echo "This script must be run as root." >&2
  exit 1
fi

# Install cron if missing
if ! command -v crontab &>/dev/null; then
  apt-get update && apt-get install -y cron
fi

# Start cron service (init.d or fallback)
if command -v service &>/dev/null; then
  service cron start || service crond start || true
elif [ -x "/etc/init.d/cron" ]; then
  /etc/init.d/cron start || true
else
  cron >/dev/null 2>&1 &
  sleep 1
fi

# Create users alice and bob, set login to home
for u in alice bob; do
  if ! id "$u" &>/dev/null; then
    useradd -m -s /bin/bash "$u"
  fi
  bashrc="/home/$u/.bashrc"
  grep -qx 'cd "$HOME"' "$bashrc" 2>/dev/null || echo 'cd "$HOME"' >> "$bashrc"
done

# Add cronjobs helper
generate_crons() {
  local user=$1 count=$2 home crontab_tmp
  home=$([[ $user == root ]] && echo "/root" || echo "/home/$user")
  crontab_tmp=$(mktemp)
  { crontab -u "$user" -l 2>/dev/null || :; } > "$crontab_tmp"

  for i in $(seq 1 "$count"); do
    minute=$(( RANDOM % 60 ))
    hour=$(( RANDOM % 24 ))
    log="$home/cronjob_${user}_${i}.log"

    # Determine schedule
    if [[ $user == root && $(( i % 2 )) -eq 0 ]]; then
      spec="$minute $hour * 1,3,5,7,9,11 2,4"
    elif [[ $user == alice && $(( i % 2 )) -eq 1 ]]; then
      spec="$minute $hour * * 1,3,5"
    elif [[ $user == bob ]]; then
      spec="$minute $hour * 2,4,6,8,10,12 0,1,3,4"
    else
      spec="$minute $hour * * *"
    fi

    # Ensure log exists
    touch "$log"
    chown "$user:$user" "$log" 2>/dev/null || true

    # Use bash -lc to ensure date substitution and environment
    echo "$spec bash -lc 'echo \"[\$(date)] ${user}_cronjob_${i} executed\" >> $log'" >> "$crontab_tmp"
  done

  # Add a fixed routine backup job for root at 11:30 IST (06:00 UTC)
  if [[ $user == root ]]; then
    echo "0 6 * * * bash -lc 'echo \"[\$(date)] routine_backup_job executed\" >> /root/cronjob_routine_backup.log'" >> "$crontab_tmp"
    touch /root/cronjob_routine_backup.log
  fi

  if [[ $user == root ]]; then
    crontab "$crontab_tmp"
  else
    crontab -u "$user" "$crontab_tmp"
  fi

  rm -f "$crontab_tmp"
}

# Generate jobs
generate_crons alice 7
generate_crons bob 6
generate_crons root 11


exec mongod \
  --bind_ip_all \
  --dbpath /data/db \
  --logpath /var/log/mongodb/mongod.log \
  --logappend
