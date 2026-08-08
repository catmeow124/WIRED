import socket
import os
import mimetypes

HOST = "127.0.0.1"
PORT = 65432

STORAGE = "STORAGE"
SERVER_NAME = "SERVER1"

SERVERS = {}
SERVERS["SERVER1"] = ("127.0.0.1", 65432)
SERVERS["SERVER2"] = ("127.0.0.1", 65433)
SERVERS["SERVER3"] = ("127.0.0.1", 65434)


def wired_to_file_path(location):
    prefix = "WIRED://" + SERVER_NAME + "/"

    if location.startswith(prefix) == False:
        raise ValueError("Location does not belong to this server :(")

    path = location[len(prefix):]
    full_path = os.path.join(STORAGE, SERVER_NAME, path)
    return full_path


def parse_request(data):
    lines = data.strip().splitlines()

    if len(lines) == 0:
        raise ValueError("Not good")

    command = lines[0].strip()
    headers = {}

    i = 1
    while i < len(lines):
        line = lines[i]
        if line == ".":
            break
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()
            headers[key] = value
        i = i + 1

    return command, headers


def request_from_server(server_name, request):
    if server_name not in SERVERS:
        raise ValueError("Unknown server: " + server_name)

    host = SERVERS[server_name][0]
    port = SERVERS[server_name][1]

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.sendall(request.encode("utf-8"))

    header_data = b""
    while b"\n.\n" not in header_data:
        data = client.recv(4096)
        if not data:
            client.close()
            raise ConnectionError("Server closed connection before headers")
        header_data = header_data + data

    header_end = header_data.find(b"\n.\n") + len(b"\n.\n")
    headers = header_data[:header_end]
    remaining_data = header_data[header_end:]

    header_text = headers.decode("utf-8")
    response_lines = header_text.splitlines()
    status = response_lines[0]

    file_size = 0
    for line in response_lines:
        if line.startswith("SIZE:"):
            file_size = int(line.split(":", 1)[1].strip())

    file_data = remaining_data
    while len(file_data) < file_size:
        data = client.recv(4096)
        if not data:
            client.close()
            raise ConnectionError("Server closed connection during file transfer :(")
        file_data = file_data + data

    file_data = file_data[:file_size]

    client.close()
    return status, header_text, file_data


def send_file_response(conn, status, location, file_path):
    file_size = os.path.getsize(file_path)
    file_type = mimetypes.guess_type(file_path)[0]
    if file_type == None:
        file_type = "application/octet-stream"

    headers = status + "\n"
    headers = headers + "LOCATION: " + location + "\n"
    headers = headers + "SIZE: " + str(file_size) + "\n"
    headers = headers + "TYPE: " + file_type + "\n"
    headers = headers + ".\n"

    conn.sendall(headers.encode("utf-8"))

    file = open(file_path, "rb")
    while True:
        chunk = file.read(4096)
        if not chunk:
            break
        conn.sendall(chunk)
    file.close()


def handle_get(conn, headers):
    location = headers.get("LOCATION")

    if not location:
        conn.sendall(b"400 BAD REQUEST\nMESSAGE: Missing LOCATION\n.\n")
        return

    try:
        file_path = wired_to_file_path(location)
    except ValueError:
        conn.sendall(b"400 BAD REQUEST\nMESSAGE: Invalid LOCATION\n.\n")
        return

    if os.path.isfile(file_path) == False:
        response = "404 NOT FOUND\nLOCATION: " + location + "\n.\n"
        conn.sendall(response.encode("utf-8"))
        return

    send_file_response(conn, "200 OK", location, file_path)


def handle_copy(conn, headers):
    source = headers.get("SOURCE")
    destination = headers.get("DESTINATION")

    if not source or not destination:
        conn.sendall(b"400 BAD REQUEST\nMESSAGE: COPY requires SOURCE and DESTINATION\n.\n")
        return

    try:
        source_split = source.split("/")
        destination_split = destination.split("/")
        source_server = source_split[2]
        destination_server = destination_split[2]
    except IndexError:
        conn.sendall(b"400 BAD REQUEST\nMESSAGE: Invalid WIRED location\n.\n")
        return

    if destination_server != SERVER_NAME:
        conn.sendall(b"400 BAD REQUEST\nMESSAGE: Destination must belong to this server\n.\n")
        return

    try:
        if source_server == SERVER_NAME:
            source_path = wired_to_file_path(source)

            if os.path.isfile(source_path) == False:
                conn.sendall(b"404 NOT FOUND\nMESSAGE: Source file does not exist\n.\n")
                return

            f = open(source_path, "rb")
            file_data = f.read()
            f.close()

        else:
            request = "GET\nLOCATION: " + source + "\n.\n"
            status, response_headers, file_data = request_from_server(source_server, request)

            if not status.startswith("200"):
                conn.sendall(response_headers.encode("utf-8"))
                return

        destination_path = wired_to_file_path(destination)

        dest_dir = os.path.dirname(destination_path)
        os.makedirs(dest_dir, exist_ok=True)

        out_file = open(destination_path, "wb")
        out_file.write(file_data)
        out_file.close()

        response = "201 CREATED\n"
        response = response + "SOURCE: " + source + "\n"
        response = response + "DESTINATION: " + destination + "\n"
        response = response + "SIZE: " + str(len(file_data)) + "\n"
        response = response + "MESSAGE: File copied good\n"
        response = response + ".\n"

        #print(response)

        conn.sendall(response.encode("utf-8"))

    except Exception as error:
        response = "500 INTERNAL SERVER ERROR\nMESSAGE: " + str(error) + "\n.\n"
        conn.sendall(response.encode("utf-8"))


def handle_client(conn, addr):
    print("Connected", addr)

    try:
        request_data = b""
        while b"\n.\n" not in request_data:
            data = conn.recv(4096)
            if not data:
                return
            request_data = request_data + data

        request_end = request_data.find(b"\n.\n") + len(b"\n.\n")
        request_text = request_data[:request_end].decode("utf-8")

        command, headers = parse_request(request_text)

        print("Command:", command)
        print("Headers:", headers)

        if command == "GET":
            handle_get(conn, headers)
        elif command == "COPY":
            handle_copy(conn, headers)
        else:
            conn.sendall(b"400 BAD REQUEST\nMESSAGE: Unknown command\n.\n")

    except Exception as error:
        print("Client error:", error)

    finally:
        print("Disconnected", addr)
        conn.close()


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    print("WIRED server", SERVER_NAME)
    print("Listening on", HOST, PORT)

    while True:
        conn, addr = s.accept()
        handle_client(conn, addr)

except Exception as server_err:
    print("Uh-Oh! Server encountered a fatal error:", server_err)

finally:
    print("Closing server...")
    s.close()
