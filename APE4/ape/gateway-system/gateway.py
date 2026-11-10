import socket
import json
from agente_ia import decidir_worker

class GatewaySystem:
    def __init__(self, red_workers):
        self.red_workers = red_workers

    def enviar_socket_tcp(self, worker_id, pedido):
        ip, puerto = self.red_workers[worker_id]
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, puerto))
            
            sock.sendall(json.dumps(pedido).encode('utf-8'))
            respuesta = sock.recv(1024).decode('utf-8')
            
            print(f"[Gateway TCP] Confirmación de Worker {worker_id}: {respuesta}")
            sock.close()
        except Exception as e:
            print(f"[Gateway TCP Error] Fallo al conectar con Worker {worker_id} ({ip}:{puerto}): {e}")

    def procesar_y_enrutar(self, pedido, estado_workers):
        print(f"\n[Gateway] Evaluando asignación para pedido {pedido['id_pedido']}...")
        decision = decidir_worker(pedido, estado_workers)
        
        target = decision.get("worker_seleccionado", "7001")
        razon = decision.get("razon", "N/A")
        
        print(f"[Gateway -> IA] Asignado a Worker_{target}. Motivo: {razon}")
        self.enviar_socket_tcp(target, pedido)