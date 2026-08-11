import socket
import shlex
import json

CONFIG_FILE = "udns_config.json"
USERS_FILE = "USERS.JSON"
HOSTS_FILE = "HOSTS.JSON"


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)


def load_hosts():
    with open(HOSTS_FILE) as f:
        return json.load(f)


def find_user(users, username):
    for u in users:
        if u["username"] == username:
            return u
    return None


def find_host(hosts, name):
    for h in hosts:
        if h["name"] == name:
            return h
    return None


def public_user_info(user):
    return {
        "id": user["id"],
        "username": user["username"],
        "last_connected": user.get("last_connected"),
        "created_at": user.get("created_at"),
    }


def send_payload(conn, obj):
    payload = json.dumps(obj)
    conn.sendall(b"OK\n")
    conn.sendall(f"{len(payload)}\n".encode())
    conn.sendall(payload.encode())


def handle_resolve(conn, target, config):
    users = load_users()

    if "@" in target:
        username, server_name = target.split("@", 1)
    else:
        username, server_name = target, config["udns_server_name"]

    if server_name != config["udns_server_name"]:
        conn.sendall(b"WRONGSERVER\n")
        return

    user = find_user(users, username)

    if user is None:
        conn.sendall(b"NOTFOUND\n")
        return

    send_payload(conn, public_user_info(user))


def handle_locate(conn, server_name):
    hosts = load_hosts()
    host = find_host(hosts, server_name)

    if host is None:
        conn.sendall(b"NOTFOUND\n")
        return

    send_payload(conn, {
        "name": host["name"],
        "address": host["address"],
        "port": host["port"],
    })


def handle_ping(conn, config):
    conn.sendall(b"PONG\n")
    conn.sendall(f"{config['udns_server_name']}\n".encode())


def main():
    config = load_config()

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((config["udns_address"], config["udns_port"]))
    server.listen(1)

    print(
        f"[*] UDNS server '{config['udns_server_name']}' listening on "
        f"{config['udns_address']}:{config['udns_port']}"
    )

    good_list = ["-RESOLVE", "-LOCATE", "-PING"]

    try:
        while True:
            conn, addr = server.accept()
            print("[*] Connected:", addr)

            try:
                data = conn.recv(1024).decode().strip()
                print("Client:", data)

                if not data.startswith("-"):
                    conn.sendall(b"ERROR\n")
                    continue

                parts = shlex.split(data)
                command = parts[0]
                arguments = parts[1:]

                print("Command:", command)
                print("Arguments:", arguments)

                if command not in good_list:
                    print("not allowed")
                    conn.sendall(b"DENIED\n")
                    continue

                if command == "-RESOLVE":
                    if len(arguments) != 1:
                        print("wrong number of args for command")
                        conn.sendall(b"ERROR\n")
                    else:
                        handle_resolve(conn, arguments[0], config)

                elif command == "-LOCATE":
                    if len(arguments) != 1:
                        print("wrong number of args for command")
                        conn.sendall(b"ERROR\n")
                    else:
                        handle_locate(conn, arguments[0])

                elif command == "-PING":
                    handle_ping(conn, config)

            except Exception as e:
                print("[!] Error:", e)
                try:
                    conn.sendall(b"ERROR\n")
                except OSError:
                    pass

            finally:
                conn.close()
                print("[*] Connection closed.")

    except KeyboardInterrupt:
        print("\n[*] UDNS server shutting down...")

    finally:
        server.close()
        print("[*] UDNS server closed.")


if __name__ == "__main__":
    main()
