import sys
import socket
import os

port = 80
if len(sys.argv) > 1:
    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Invalid port number.")
        sys.exit(1)

def get_content_type(filename):
    ext = os.path.splitext(filename)[1]
    content_types = {
        ".html": "text/html",
        ".css":  "text/css",
        ".js":   "application/javascript",
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".txt":  "text/plain",
    }
    return content_types.get(ext, "application/octet-stream")

def build_response(filename):
    try:
        with open(filename, "rb") as file:
            content = file.read()
        content_type = get_content_type(filename)
        header = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(content)}\r\n"
            f"\r\n"
        ).encode()
        return header + content
    except FileNotFoundError:
        body = b"<h1>404 Not Found</h1><p>The requested file was not found on this server.</p>"
        header = (
            f"HTTP/1.1 404 Not Found\r\n"
            f"Content-Type: text/html\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"\r\n"
        ).encode()
        return header + body

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', port))
server_socket.listen(1)
print(f"Server is listening on port {port}...")

while True:
    try:
        conn_socket, addr = server_socket.accept()
        print(f"Connection from {addr} has been established.")

        request = conn_socket.recv(1024).decode()
        print(f"Received request:\n{request}")

        first_line = request.split("\n")[0]
        filename = first_line.split(" ")[1].lstrip("/")

        # Default to index.html if no file specified
        if not filename:
            filename = "index.html"

        response = build_response(filename)
        conn_socket.sendall(response)
        conn_socket.close()

    except KeyboardInterrupt:
        print("\nShutting down the server.")
        server_socket.close()
        sys.exit(0)

server_socket.close()