import time
import random
import json

def generar_pedidos(queue, num_pedidos=5):
    """
    Genera pedidos simulados de delivery y los inserta en la Queue de IPC.
    """
    for i in range(1, num_pedidos + 1):
        pedido = {
            "id_pedido": f"PED-{100 + i}",
            "distancia_km": round(random.uniform(1.0, 12.0), 2),
            "prioridad": random.choice(["ALTA", "MEDIA", "BAJA"]),
            "items": random.randint(1, 6)
        }
        print(f"[IPC - Productor] Pedido generado: {pedido['id_pedido']} ({pedido['distancia_km']} km)")
        queue.put(json.dumps(pedido))
        time.sleep(1)