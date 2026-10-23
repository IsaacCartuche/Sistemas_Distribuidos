import multiprocessing
import time
import random

def productor_main(queue):
    while True:
        data = {
            "temp": random.uniform(20, 100),
            "vib": random.uniform(0, 10),
            "timestamp": time.time()
        }
        print("[IPC-Productor]", data)
        queue.put(data)
        time.sleep(1) 