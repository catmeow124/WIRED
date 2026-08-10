import socket

client = socket.socket()
client.connect(("localhost", 5000))

client.sendall(b'-FETCH "WIRED://SERVER1/INDEX.WD"')

data = client.recv(1024)
print("Server:", data.decode())

client.close()
