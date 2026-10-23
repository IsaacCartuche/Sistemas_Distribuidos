import socket
import json
import time

def cliente(memoria):
    HOST = "127.0.0.1"
    PORT = 6000

    while True:
        if "data" in memoria:
            data = memoria["data"]

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT))
                s.send(json.dumps(data).encode())
                s.close()

                print("[CLIENTE] Enviado:", data)
            except:
                print("[CLIENTE] Error conexión")

        time.sleep(2)