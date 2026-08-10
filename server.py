import socket
import shlex
import os

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 5000))
server.listen(1)

STORAGE = "STORAGE"
SERVER_NAME = "SERVER1"


def fetch(conn, path):
    file_path = wired_path(path)

    file_size = os.path.getsize(file_path)

    conn.sendall(f"{file_size}\n".encode())

    with open(file_path, "rb") as f:
        while True:
            fetch_data = f.read(4096)

            if not fetch_data:
                break

            conn.sendall(fetch_data)

def wired_path(location):
    prefix = "WIRED://" + SERVER_NAME + "/"

    if not location.startswith(prefix):
        raise ValueError("Location does not belong to this server :(")

    path = location[len(prefix):]

    base_path = os.path.abspath(
        os.path.join(STORAGE, SERVER_NAME)
    )

    full_path = os.path.abspath(
        os.path.join(base_path, path)
    )

    if os.path.commonpath([base_path, full_path]) != base_path:
        raise ValueError("Path escapes server storage")

    return full_path


conn, addr = server.accept()
print("[*] Connected:", addr)

data = conn.recv(1024).decode().strip()
print("Client:", data)

if data.startswith("-"):
    parts = shlex.split(data)

    command = parts[0]
    arguments = parts[1:]

    print("Command:", command)
    print("Arguments:", arguments)

    if command == "#":
        pass

    if command == "-FETCH":
        if len(arguments) != 1:
            print("wrong number of args for command")
        else:
            print("good fetch")
            fetch(conn, arguments[0])


conn.close()
server.close()
