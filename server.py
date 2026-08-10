import socket
import shlex
import os

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 5000))
server.listen(1)

STORAGE = "STORAGE"
SERVER_NAME = "SERVER1"

def wired_path(location):
    prefix = "WIRED://" + SERVER_NAME + "/"

    if location.startswith(prefix) == False:
        raise ValueError("Location does not belong to this server :(")

    path = location[len(prefix):]
    full_path = os.path.join(STORAGE, SERVER_NAME, path)
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

    if command == "-FETCH":
        if len(arguments) > 1:
            print("to many args for command")
        else:
            print("good fetch")
            with open(wired_path(arguments[0])) as f:
                print(f.read()) 
conn.sendall(b"Hello from server!")

conn.close()
server.close()
