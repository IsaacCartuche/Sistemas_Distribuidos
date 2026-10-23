import socket
import json
import threading
import requests

HOST = "0.0.0.0"
PORT = 6000

servidores = [("127.0.0.1", 7001), ("127.0.0.1", 7002)]
indice = 0
lock = threading.Lock()

# 🔹 IA con Ollama
def decision_ia(data):
    print("gateway data")
    print(data)
    try:
        
        prompt = f"Clasifica este dato como CRITICO o NORMAL: {data}"

        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "codegeex4",
            "prompt": prompt,
            "stream": False
        })

        resultado = response.json()["response"]

        if "CRITICO" in resultado.upper():
            return 0
        return 1

    except:
        print("[IA] Error, usando Round Robin")
        return None


def enviar(destino, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(destino)
        s.send(json.dumps(data).encode())
        s.close()

        print("[GATEWAY] Enviado a", destino)
    except Exception as e:
        print("[ERROR GATEWAY]", e)


def manejar_cliente(conn, addr):
    global indice

    data = conn.recv(1024)

    if data:
        decoded = json.loads(data.decode())

        # 🔥 DECISIÓN IA
        idx = decision_ia(decoded)

        if idx is None:
            # fallback → Round Robin
            with lock:
                idx = indice
                indice = (indice + 1) % len(servidores)

        destino = servidores[idx]

        print("[GATEWAY] Cliente", addr, "→", destino)

        enviar(destino, decoded)

    conn.close()


def gateway():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print("[GATEWAY] activo...")

    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    gateway()