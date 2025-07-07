# server.py
import socket
import threading

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True:
            # Blocking recv: will wake whenever client sends
            data = conn.recv(1024)
            if not data:
                # client has closed the socket; break out and end thread
                print(f"[DISCONNECTED] {addr} has closed the connection.")
                break

            text = data.decode('utf-8', errors='ignore')
            print(f"[{addr}] Message: {text}")

            # Echo back (or you could do other processing)
            conn.sendall(f"Server received: {text}".encode('utf-8'))
    except Exception as e:
        print(f"[ERROR] {addr}: {e!r}")
    finally:
        conn.close()
        print(f"[THREAD END] {addr} handler exiting.")

def start_server(host='127.0.0.1', port=65432):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow quick restart
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    print(f"[SERVER] Listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
