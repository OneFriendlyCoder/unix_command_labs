#!/bin/bash
set -euo pipefail

PID_FILE="/home/.evaluationScripts/python_processes.pids"
: > "${PID_FILE}"

launch() {
  nohup "$@" >/dev/null 2>&1 &
  echo $! >> "${PID_FILE}"
  # don’t disown: we want to be able to wait on them
}

# Launch all three
launch python3 /home/.evaluationScripts/tcp_connection_server.py
sleep 5
launch python3 /home/.evaluationScripts/tcp_connection_client.py
launch python3 /home/.evaluationScripts/udp_connection.py

printf "\nAll scripts launched. PIDs saved in %s:\n\n" "${PID_FILE}"
cat "${PID_FILE}"

# Now wait for each child PID to exit:
while read -r pid; do
  echo "Waiting on PID ${pid}..."
  wait "${pid}"
  echo "Process ${pid} has exited."
done < "${PID_FILE}"