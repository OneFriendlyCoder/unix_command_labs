#!/usr/bin/env python3
import os
import http.server
import socketserver

# Hardcoded file name and port
FILE_NAME = "/home/.evaluationScripts/index.html"
PORT = 30002

class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Custom HTTP Request Handler to serve only the 'index.html' file.
    """
    def do_GET(self):
        if self.path == "/index.html":
            try:
                # Serve the index.html file
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
    Run a simple HTTP server on the hardcoded port, serving only the 'index.html' file.
    """
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serving file '{FILE_NAME}' on localhost port {PORT} (http://localhost:{PORT}/index.html) ...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
