import socket
import threading
import os
import sys
import signal
import mimetypes
from http import HTTPStatus
from datetime import datetime
from urllib.parse import unquote

# Constants
DEFAULT_HOST = ''  # localhost
DEFAULT_PORT = 8080  # default port
WEBROOT = 'www'  # root dir
BUFFER_SIZE = 1024

server_socket = None
running = False

# Response header helper function


def create_response_header(
    status_code,
    content_type=None,
    content_length=None
):
    header = f"HTTP/1.1 {status_code.value} {status_code.phrase}\r\n"
    if content_type:
        header += f"Content-Type: {content_type}\r\n"
    if content_length is not None:
        header += f"Content-Length: {content_length}\r\n"
    header += "Connection: close\r\n"
    header += "\r\n"
    return header.encode()  # defaults to UTF-8


# Content type obtainment helper function
def get_content_type(file_path):
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or "application/octet-stream"


# Logger
def log_request(client_ip, method, path, version, status_code):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(
        f'{client_ip} - - [{now}] "{method} {path} {version}" {status_code.value} - {status_code.phrase}'
    )


# Main request handler
def handle_request(client_socket, client_address):
    try:
        request = b""

        while True:
            part = client_socket.recv(BUFFER_SIZE)
            if not part:
                break
            request += part

            if b"\r\n\r\n" in request:
                break

        if not request:
            client_socket.close()
            return

        request_line = request.split(b'\r\n', 1)[0].decode()  # get first line
        parts = request_line.split()
        if len(parts) < 3:
            client_socket.sendall(
                create_response_header(HTTPStatus.BAD_REQUEST))
            client_socket.close()
            log_request(client_address[0], 'UNKNOWN', 'UNKNOWN', 'UNKNOWN',
                        HTTPStatus.BAD_REQUEST)
            return

        method, raw_path, version = parts
        path = unquote(raw_path.split('?', 1)[0])  # remove query param
        client_ip = client_address[0]
        response_code = HTTPStatus.OK  # default, will be updated by code if needed

        if method != 'GET':
            response_code = HTTPStatus.METHOD_NOT_ALLOWED
            client_socket.sendall(create_response_header(response_code))
            client_socket.close()
            log_request(client_ip, method, path, version, response_code)
            return

        if path == '/':
            path = '/index.html'

        safe_path = os.path.normpath(path).lstrip(os.sep)  # normalize path
        full_path = os.path.join(WEBROOT, safe_path)

        if os.path.isdir(full_path):
            full_path = os.path.join(full_path, "index.html")

        if not os.path.isfile(full_path):
            error_path = os.path.join(WEBROOT, '404', 'index.html')
            if os.path.isfile(error_path):
                with open(error_path, 'rb') as f:
                    body = f.read()
            else:
                body = b"<html><body><h1>404 Not Found</h1></body></html>"
            response_code = HTTPStatus.NOT_FOUND
            client_socket.sendall(
                create_response_header(response_code, 'text/html', len(body)) +
                body)
            client_socket.close()
            log_request(client_ip, method, path, version, response_code)
            return

        with open(full_path, 'rb') as f:
            body = f.read()

        content_type = get_content_type(full_path)
        client_socket.sendall(
            create_response_header(response_code, content_type, len(body)) +
            body)
        client_socket.close()
        log_request(client_ip, method, path, version, response_code)

    except Exception as e:
        print(
            f"[Server] Error, failed to read request from {client_address}: {e}"
        )
        response_code = HTTPStatus.INTERNAL_SERVER_ERROR
        client_socket.sendall(create_response_header(response_code))
        client_socket.close()
        return


# Handling interrupt signal to gracefully shut down the server
def signal_handler(signal, frame):
    global running, server_socket
    if not running:
        return

    print('[Server] Closing the server... (Ctrl+C pressed)')

    running = False
    if server_socket:
        server_socket.close()
        print('[Server] Server closed successfully.')
    sys.exit(0)


# Server initialization function
def init():
    global server_socket, running
    signal.signal(signal.SIGINT, signal_handler)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # equivalent to .allow_reuse_address = True
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((DEFAULT_HOST, DEFAULT_PORT))
    server_socket.listen(5)
    running = True

    print(f"[Server] Listening on {DEFAULT_HOST}:{DEFAULT_PORT}...")
    print("[Server] Press Ctrl+C to stop the server.")

    while running:
        try:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_request,
                             args=(client_socket, client_address)).start()
        except OSError:
            break

    print("[Server] Server is shutting down...")


if __name__ == "__main__":
    init()
