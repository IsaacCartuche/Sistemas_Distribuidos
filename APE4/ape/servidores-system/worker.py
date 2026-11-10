import socket
import json
import sys
import time

def iniciar_worker(puerto, host='0.0.0.0'):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, puerto))
        server_socket.listen(5)
        print(f"[WORKER EN LÍNEA] Escuchando en puerto: {puerto}")

        while True:
            conn, addr = server_socket.accept()
            data = conn.recv(2048).decode('utf-8')
            
            if data:
                pedido = json.loads(data)
                print(f"\n[Worker {puerto}] Recibido Pedido: {pedido.get('id_pedido')} ({pedido.get('distancia_km')} km)")
                time.sleep(1.5)
                
                respuesta = {
                    "status": "COMPLETADO",
                    "nodo": puerto,
                    "id_pedido": pedido.get('id_pedido')
                }
                conn.sendall(json.dumps(respuesta).encode('utf-8'))
            
            conn.close()
    except KeyboardInterrupt:
        print("\n[Worker] Deteniendo servidor...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 7001
    iniciar_worker(puerto)