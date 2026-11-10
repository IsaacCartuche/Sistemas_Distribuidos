import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# CONFIGURAR parámetros MQTT
BROKER = "localhost"
PORT = 1883
VEHICULOS = ["VH-001", "VH-002", "VH-003"]

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback al conectarse al broker MQTT."""
    print(f"[{datetime.now().isoformat()}] Conectado al broker MQTT (rc={rc})")

def simular_gps(id_vehiculo):
    """Simula datos de ubicación GPS y velocidad."""
    base_lat = -2.1709
    base_lng = -79.9224
    
    latitud = base_lat + random.uniform(-0.01, 0.01)
    longitud = base_lng + random.uniform(-0.01, 0.01)
    velocidad = random.uniform(20, 80)
    
    return {
        "lat": round(latitud, 6),
        "lng": round(longitud, 6),
        "speed": round(velocidad, 1)
    }

def simular_temperatura(id_vehiculo):
    """Simula la temperatura del compartimento de carga (-5 a 8 °C)."""
    temperatura = random.uniform(-5, 8)
    return {
        "temperature": round(temperatura, 1),
        "unit": "celsius"
    }

def simular_combustible(id_vehiculo):
    """Simula el nivel de combustible (10 a 100 %)."""
    combustible = random.uniform(10, 100)
    return {
        "fuel_level": round(combustible, 1),
        "unit": "percent"
    }

def principal():
    """Función principal para inicializar y ejecutar la simulación."""
    client = mqtt.Client()
    client.on_connect = on_connect
    
    # Conectar al broker e iniciar loop
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    
    print("Iniciando simulador de sensores IoT...")
    
    try:
        while True:
            for vehiculo in VEHICULOS:
                timestamp = datetime.now().isoformat()
                
                # --- Sensor GPS ---
                gps_info = simular_gps(vehiculo)
                datos_gps = {
                    "vehicle_id": vehiculo,
                    "timestamp": timestamp,
                    **gps_info
                }
                client.publish(f"flota/{vehiculo}/gps", json.dumps(datos_gps))
                
                # --- Sensor Temperatura ---
                temp_info = simular_temperatura(vehiculo)
                datos_temp = {
                    "vehicle_id": vehiculo,
                    "timestamp": timestamp,
                    **temp_info
                }
                client.publish(f"flota/{vehiculo}/temperatura", json.dumps(datos_temp))
                
                # --- Sensor Combustible ---
                fuel_info = simular_combustible(vehiculo)
                datos_fuel = {
                    "vehicle_id": vehiculo,
                    "timestamp": timestamp,
                    **fuel_info
                }
                client.publish(f"flota/{vehiculo}/combustible", json.dumps(datos_fuel))
                
                print(f"[{timestamp}] Datos publicados para vehiculo {vehiculo}")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\nDeteniendo simulador...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    principal()