import socket

client = socket.socket()
client.connect(("localhost", 5000))

client.sendall(b'-FETCH "WIRED://SERVER1/INDEX.WD"')

header = b""

while not header.endswith(b"\n"):
    data = client.recv(1)

    if not data:
        break

    header += data


file_size = int(header.decode().strip())

print("File size:", file_size, "bytes")

received = 0

with open("INDEX.WD", "wb") as f:
    while received < file_size:
        data = client.recv(min(4096, file_size - received))

        if not data:
            break

        f.write(data)
        received += len(data)


print("Received:", received, "bytes")

client.close()
