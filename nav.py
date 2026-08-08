import socket
import re
import os
import sys


HOST = "127.0.0.1"
PORT = 65432
entered = {}

def get(location):
    request = f"""GET
LOCATION: {location}
.
"""


    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as s:

        s.connect((HOST, PORT))

        s.sendall(
            request.encode()
        )

        data = b""
        while b"\n.\n" not in data:
            data = data + s.recv(4096)

        header_end = data.find(b"\n.\n") + len(b"\n.\n")
        headers = data[:header_end].decode()
        content = data[header_end:]

        size = 0
        for line in headers.splitlines():
            if line.startswith("SIZE:"):
                size = int(line.split(":", 1)[1].strip())

        while len(content) < size:
            content = content + s.recv(4096)


    return headers, content.decode()

def navigate(location):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        headers, content = get(location)

        if not headers.startswith("200 OK"):
            print(headers)
            return

        print("=" * 50)
        print(location)
        print("=" * 50)

        print(content)

        links = re.findall(
            r"\[([^\]]+)\]\s+(WIRED://\S+)",
            content
        )

        for i, (name, target) in enumerate(
            links,
            start=1
        ):
            print(f"[{i}] {name}")

        print("[?] HELP")

        choice = input("\n>")
        
        if choice.lower() == "q":
            sys.exit(0)

        if choice.lower() == "g":
            g_loc = input("\nGoTo>")
            location = g_loc

        if choice.lower() == "?":
            print("--HELP MENU--")
            print("[Q] QUIT (Closes navigator)")
            print("[G] GOTO (Displays location prompt)")
            blank = input("Press <ENTER> to continue")
    
        if choice.isdigit():
            try:
                index = int(choice) - 1
                location = links[index][1]

            except (ValueError, IndexError):
                print("Error :(\nBad selection.")

navigate("WIRED://SERVER1/GLOBAL/FILES/INDEX.WD")
