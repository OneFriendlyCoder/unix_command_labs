import socket
import random
import time

UDP_SOCKETS = []

def get_random_port():
    return random.randint(10000, 60000)

def create_udp_listener(port=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = port or get_random_port()
    sock.bind(('127.0.0.1', port))
    print(f"[LISTENING] UDP socket bound to 127.0.0.1:{port}")
    return sock

def create_udp_sender(remote_port=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = remote_port or get_random_port()
    try:
        sock.connect(('127.0.0.1', port))  # This doesn't establish a connection; just sets default addr
        print(f"[SENDER] UDP socket 'connected' to 127.0.0.1:{port}")
    except Exception as e:
        print(f"[ERROR] Couldn't connect: {e}")
    return sock

def main():
    num_listeners = 4  # e.g., 4 listening sockets
    num_senders = 6    # e.g., 6 sending sockets

    # Create listening sockets
    for _ in range(num_listeners):
        sock = create_udp_listener()
        UDP_SOCKETS.append(sock)

    # Create sender sockets
    for _ in range(num_senders):
        sock = create_udp_sender()
        UDP_SOCKETS.append(sock)

    print(f"\n[INFO] Total {len(UDP_SOCKETS)} UDP sockets created.")
    print("[INFO] Press Ctrl+C to close them and exit.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Closing all sockets.")
        for sock in UDP_SOCKETS:
            sock.close()

if __name__ == "__main__":
    main()
