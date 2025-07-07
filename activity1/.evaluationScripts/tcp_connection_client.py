# client.py
import socket
import threading
import time
import random

def client_thread(client_id, host='127.0.0.1', port=65432):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[CLIENT-{client_id}] Connected to server.")

    try:
        while True:
            # wait a random time between 1 and 10 seconds
            t = random.uniform(1.0, 10.0)
            time.sleep(t)

            # send a timestamped or sequential message
            msg = f"Client-{client_id} says hello at {time.time():.2f}"
            sock.sendall(msg.encode('utf-8'))
            print(f"[CLIENT-{client_id}] Sent: {msg}")

            # non-blocking check for server reply
            sock.settimeout(0.5)
            try:
                resp = sock.recv(1024)
                if resp:
                    print(f"[CLIENT-{client_id}] Received: {resp.decode('utf-8')}")
            except socket.timeout:
                # no reply yet
                pass
            finally:
                # restore blocking
                sock.settimeout(None)
    except Exception as e:
        print(f"[CLIENT-{client_id}] Error: {e!r}")
    finally:
        sock.close()
        print(f"[CLIENT-{client_id}] Exiting.")

def spawn_clients(num_clients=10):
    threads = []
    for i in range(1, num_clients + 1):
        t = threading.Thread(target=client_thread, args=(i,), daemon=True)
        threads.append(t)
        t.start()
        # slight stagger on startup
        time.sleep(0.2)

    # main thread just waits forever
    print(f"[CLIENT MANAGER] Spawned {num_clients} clients; running indefinitely.")
    threading.Event().wait()

if __name__ == "__main__":
    spawn_clients(10)
