import socket
import shlex
import os
import json

with open("server_config.json") as f:
    CONFIG = json.load(f)

SERVER_NAME = CONFIG["server_name"]
STORAGE = "STORAGE"
good_list = ["-FETCH"]

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((CONFIG["address"], CONFIG["port"]))
server.listen(1)

def fetch(conn, path):
    try:
        file_path = wired_path(path)
    except ValueError as e:
        print("Bad path:", e)
        conn.sendall(b"DENIED\n")
        return

    if not os.path.isfile(file_path):
        print("File not found:", file_path)
        conn.sendall(b"NOTFOUND\n")
        return

    file_size = os.path.getsize(file_path)
    conn.sendall(b"OK\n")
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


print(f"[*] WIRED server '{SERVER_NAME}' listening on {CONFIG['address']}:{CONFIG['port']}")

try:
    while True:

        conn, addr = server.accept()
        print("[*] Connected:", addr)

        try:

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

                if command in good_list:
                    if command == "-FETCH":
                        if len(arguments) != 1:
                            print("wrong number of args for command")
                            conn.sendall(b"ERROR\n")
                        else:
                            print("good fetch")
                            fetch(conn, arguments[0])
                else:
                        print("not allowed")
                        conn.sendall(b"DENIED\n")

        except Exception as e:
            print("[!] Error:", e)

        finally:
            conn.close()
            print("[*] Connection closed.")

except KeyboardInterrupt:
    print("\n[*] Server shutting down...")

finally:
    server.close()
    print("[*] Server closed.")
