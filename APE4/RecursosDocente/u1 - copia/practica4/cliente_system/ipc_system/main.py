import multiprocessing
import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ipc_system.controls.productor as productor
import ipc_system.controls.procesador as procesador
def iniciar_ipc():
    manager = multiprocessing.Manager()
    queue = multiprocessing.Queue() 
    memoria = manager.dict()

    p1 = multiprocessing.Process(target=productor.productor_main, args=(queue,))
    p2 = multiprocessing.Process(target=procesador.procesador_main, args=(queue, memoria))

    p1.start()
    p2.start()

    return memoria