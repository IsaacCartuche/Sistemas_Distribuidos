from multiprocessing import Process, Queue
import time
import json
import sys
import os

# Ajuste de rutas relativas según el árbol de tu proyecto
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_APE = os.path.abspath(os.path.join(DIRECTORIO_ACTUAL, ".."))

# Agregar carpetas al PATH de Python
sys.path.append(os.path.join(DIRECTORIO_ACTUAL, 'ipc_system', 'controls'))
sys.path.append(os.path.join(RAIZ_APE, 'gateway-system'))
sys.path.append(DIRECTORIO_ACTUAL)

from productor import generar_pedidos
from procesador import procesar_pedidos
from gateway import GatewaySystem
from cliente import ClienteSystem

def main():
    print("==================================================")
    print("INICIANDO SISTEMA DISTRIBUIDO (APE 4)")
    print("==================================================")

    # 1. Colas IPC
    cola_bruta = Queue()
    cola_procesada = Queue()

    # 2. Configuración de trabajadores TCP
    red_workers = {
        "7001": ("127.0.0.1", 7001),  # Cambiar por IP real si usas otra máquina
        "7002": ("127.0.0.1", 7002)
    }

    # 3. Estado dinámico de los nodos
    estado_workers = {
        "7001": {"carga": 2, "distancia": 3.0},
        "7002": {"carga": 0, "distancia": 7.5}
    }

    # 4. Inicializar componentes
    gateway = GatewaySystem(red_workers)
    cliente = ClienteSystem(gateway)

    # 5. Iniciar procesos IPC
    p_productor = Process(target=generar_pedidos, args=(cola_bruta, 3))
    p_procesador = Process(target=procesar_pedidos, args=(cola_bruta, cola_procesada))

    p_productor.start()
    p_procesador.start()

    # 6. Bucle principal de transmisión
    pedidos_atendidos = 0
    while pedidos_atendidos < 3:
        if not cola_procesada.empty():
            data = cola_procesada.get()
            if data == "FIN":
                break
            
            pedido = json.loads(data)
            cliente.enviar_al_gateway(pedido, estado_workers)
            
            # Actualización simulada de la carga
            estado_workers["7001"]["carga"] += 1
            pedidos_atendidos += 1
        time.sleep(0.5)

    p_productor.join()
    p_procesador.join()
    print("\n[Sistema Central] Proceso completado exitosamente.")

if __name__ == "__main__":
    main()


