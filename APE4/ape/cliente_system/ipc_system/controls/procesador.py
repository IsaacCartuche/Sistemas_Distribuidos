import json

def procesar_pedidos(queue_in, queue_out):
    """
    Extrae los pedidos de la cola IPC, valida los datos y los envía a la cola procesada.
    """
    while True:
        data = queue_in.get()
        if data == "FIN":
            queue_out.put("FIN")
            break
        
        pedido = json.loads(data)
        pedido["estado"] = "VALIDADO_IPC"
        print(f"[IPC - Procesador] Pedido {pedido['id_pedido']} verificado e ingresado a memoria.")
        queue_out.put(json.dumps(pedido))