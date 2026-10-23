def procesador_main(queue, memoria):
    while True:
        data = queue.get()

        # Lógica avanzada
        data["alerta"] = data["temp"] > 75 or data["vib"] > 7

        memoria["data"] = data

        print("[IPC-Procesador]", data) 