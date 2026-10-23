import socket
import json
import sys

def servidor_base(puerto):
    HOST = "0.0.0.0"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, puerto))
    s.listen()

    print(f"[SERVIDOR {puerto}] activo...")

    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)

        if data:
            decoded = json.loads(data.decode())
            print(f"[SERVIDOR {puerto}] Recibido:", decoded)

        conn.close()

if __name__ == "__main__":
    puerto = int(sys.argv[1])
    servidor_base(puerto)
