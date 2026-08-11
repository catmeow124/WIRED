import os
import shlex
from connector import *

CACHE = "FILES/"

def parse_wd(name):
    with open(name, "r") as f:
        content = f.read()

    if not content.startswith("**WD"):
        return

    links = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            parts = shlex.split(line)
            if len(parts) >= 4 and parts[2] == "=":
                display_text = parts[1]
                target = parts[3]
                links.append((display_text, target))
                index = len(links)
                print(f"[{index}] {display_text} -> {target}")

    return links

def navigate(location):
    name = CACHE + location.rsplit("/", 1)[-1]
    extension = name.rsplit(".", 1)[-1]
    ok = fetch(location, name)
    if not ok:
        print(f"bad fetch {location}")
        return
    if extension == "WD":
        return parse_wd(name)

def main():
    while True:
        choice = input(">")
        parts = shlex.split(choice)
        if not parts:
            continue
        if parts[0] == "WHOIS":
            resolve(parts[1])
        elif parts[0] == "GOTO":
            navigate(parts[1])
        

main()
