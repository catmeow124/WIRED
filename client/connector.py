import socket
import json
import sys
import shlex

UDNS_CONFIG_FILE = "udns_config.json"


def start_client(location):
    address, port, real_location = resolve_target(location)
    client = socket.socket()
    client.connect((address, port))
    return client, address, port, real_location


def close_client(client):
    client.close()
    sys.exit(0)


def load_udns_config():
    with open(UDNS_CONFIG_FILE) as f:
        return json.load(f)


def read_line(sock):
    line = b""
    while not line.endswith(b"\n"):
        data = sock.recv(1)
        if not data:
            break
        line += data
    return line.decode().strip()


def read_exact(sock, size):
    payload = b""
    while len(payload) < size:
        chunk = sock.recv(size - len(payload))
        if not chunk:
            break
        payload += chunk
    return payload


def locate_server(server_name):
    udns_config = load_udns_config()
    sock = socket.socket()
    sock.connect((udns_config["udns_address"], udns_config["udns_port"]))
    sock.sendall(f'-LOCATE "{server_name}"'.encode())
    status = read_line(sock)
    if status != "OK":
        sock.close()
        raise LookupError(f"UDNS could not locate '{server_name}': {status}")
    size = int(read_line(sock))
    payload = read_exact(sock, size)
    sock.close()
    return json.loads(payload.decode())


def resolve(username_at_server):
    config = load_udns_config()
    sock = socket.socket()
    sock.connect((config["udns_address"], config["udns_port"]))
    sock.sendall(f'-RESOLVE "{username_at_server}"'.encode())
    status = read_line(sock)
    print("UDNS server:", status)
    if status == "OK":
        size = int(read_line(sock))
        payload = read_exact(sock, size)
        info = json.loads(payload.decode())
        print("User info:", info)
        sock.close()
        return info
    elif status == "NOTFOUND":
        print("No such user.")
    elif status == "WRONGSERVER":
        print("That user isn't on this UDNS server.")
    elif status == "DENIED":
        print("Command denied.")
    else:
        print("Unknown response:", status)
    sock.close()
    return None


def ping():
    config = load_udns_config()
    sock = socket.socket()
    sock.connect((config["udns_address"], config["udns_port"]))
    sock.sendall(b"-PING")
    status = read_line(sock)
    if status == "PONG":
        name = read_line(sock)
        print(f"UDNS server alive: {name}")
    else:
        print("Unexpected response:", status)
    sock.close()


def parse_location(location):
    prefix = "WIRED://"
    if not location.startswith(prefix):
        raise ValueError("not a WIRED location")
    rest = location[len(prefix):]
    parts = rest.split("/", 1)
    if len(parts) != 2:
        raise ValueError("bad WIRED location, expected WIRED://SERVERNAME/PATH")
    return parts[0], parts[1]


def resolve_target(location):
    server_name, _ = parse_location(location)
    host_info = locate_server(server_name)
    return host_info["address"], host_info["port"], location

def fetch(location, output_path=None):
    client, address, port, real_location = start_client(location)
    print(f"Resolved to {address}:{port} -> {real_location}")
    client.sendall(f'-FETCH "{real_location}"'.encode())
    status = read_line(client)
    print("Server:", status)
    if status == "OK":
        header = read_line(client)
        file_size = int(header)
        print("File size:", file_size, "bytes")
        if output_path is None:
            output_path = real_location.rsplit("/", 1)[-1]
        received = 0
        with open(output_path, "wb") as f:
            while received < file_size:
                data = client.recv(min(4096, file_size - received))
                if not data:
                    break
                f.write(data)
                received += len(data)
        print("Received:", received, "bytes ->", output_path)
        client.close()
        return True
    elif status == "NOTFOUND":
        print(f"No such file: {real_location}")
    elif status == "DENIED":
        print("The server denied the command.")
    else:
        print("Unknown server response:", status)
    client.close()
    return False
