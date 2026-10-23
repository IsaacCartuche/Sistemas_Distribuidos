import sys
import os
from cliente import cliente
import threading
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ipc_system.main import iniciar_ipc


if __name__ == "__main__":
    memoria = iniciar_ipc()

    num_clientes = 3

    for i in range(num_clientes):
        t = threading.Thread(target=cliente, args=(memoria,))
        t.start()