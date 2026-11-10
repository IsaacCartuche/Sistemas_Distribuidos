import json

class ClienteSystem:
    def __init__(self, gateway):
        self.gateway = gateway

    def enviar_al_gateway(self, pedido, estado_workers):
        print(f"[Cliente] Transfiriendo pedido {pedido['id_pedido']} al Gateway...")
        self.gateway.procesar_y_enrutar(pedido, estado_workers)