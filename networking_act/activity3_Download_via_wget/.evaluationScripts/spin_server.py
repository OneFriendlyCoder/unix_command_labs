#!/usr/bin/env python3
import os
import http.server
import socketserver

# Hardcoded file name and port
FILE_NAME = "/home/.evaluationScripts/system_update"
PORT = 30001
FILE_SIZE = 100 * 1024 * 1024  # 100MB in bytes
TEXT_DATA = "This is a system update file. "  # 32 bytes per repetition

def create_dummy_file():
    """
    Create a 'system_update' file of 100MB filled with text data if it does not already exist.
    """
    if not os.path.isfile(FILE_NAME) or os.path.getsize(FILE_NAME) != FILE_SIZE:
        print(f"Creating file '{FILE_NAME}' with size 100MB and text content...")
        with open(FILE_NAME, "w") as f:
            while f.tell() < FILE_SIZE:
                f.write(TEXT_DATA)
        print(f"File '{FILE_NAME}' created with textual data.")
    else:
        print(f"File '{FILE_NAME}' already exists with the correct size.")

class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Custom HTTP Request Handler to serve only the 'system_update' file.
    """
    def do_GET(self):
        if self.path == "/system_update":
            try:
                # Serve the system_update file
                with open(FILE_NAME, 'rb') as f:
                    file_content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/octet-stream')
                    self.send_header('Content-Length', str(len(file_content)))
                    self.end_headers()
                    self.wfile.write(file_content)
            except FileNotFoundError:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "Not Found")

def run_server():
    """
    Run a simple HTTP server on the hardcoded port, serving only the 'system_update' file.
    """
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving file '{FILE_NAME}' on localhost port {PORT} (http://localhost:{PORT}/system_update) ...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    create_dummy_file()
    run_server()
