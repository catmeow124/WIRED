import socket


HOST = "127.0.0.1"
PORT = 65432

copy_request = """COPY
TITLE: HELLO WORLD
DESCRIPTION: HELLO WORLD TEXT FILE
SOURCE: WIRED://SERVER2/GLOBAL/FILES/HELLO.TXT
DESTINATION: WIRED://SERVER1/GLOBAL/FILES/HELLO.TXT
.
"""


with socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
) as s:

    s.connect((HOST, PORT))

    print("Sending COPY request:")
    print(copy_request)

    s.sendall(
        copy_request.encode("utf-8")
    )

    data = b""
    while b"\n.\n" not in data:
        data = data + s.recv(4096)

    print("COPY response:")
    print(data.decode("utf-8"))

FETCH_request = """FETCH
LOCATION: WIRED://SERVER1/GLOBAL/FILES/HELLO.TXT
.
"""


with socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
) as s:

    s.connect((HOST, PORT))

    print("Sending FETCH request:")
    print(FETCH_request)

    s.sendall(
        FETCH_request.encode("utf-8")
    )

    data = b""
    while b"\n.\n" not in data:
        data = data + s.recv(4096)

    header_end = data.find(b"\n.\n") + len(b"\n.\n")
    headers = data[:header_end].decode("utf-8")
    file_data = data[header_end:]

    print("FETCH headers:")
    print(headers)

    file_size = 0
    for line in headers.splitlines():
        if line.startswith("SIZE:"):
            file_size = int(line.split(":", 1)[1].strip())

    while len(file_data) < file_size:
        file_data = file_data + s.recv(4096)

    print("FETCH returned:")
    print(file_data.decode("utf-8"))

print("it works! :D")
