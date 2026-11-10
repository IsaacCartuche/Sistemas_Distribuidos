import json
import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt

# CONFIGURACIÓN
BROKER = "localhost"
PORT = 1883
DB_NAME = "telemetria.db"

def inicializar_base_datos():
    """Crea la base de datos y las 3 tablas requeridas si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla para datos de GPS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            lat REAL,
            lng REAL,
            speed REAL,
            timestamp TEXT
        )
    ''')
    
    # Tabla para datos de Temperatura
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            temperature REAL,
            unit TEXT,
            timestamp TEXT
        )
    ''')
    
    # Tabla para datos de Combustible
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuel_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            fuel_level REAL,
            unit TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Base de datos 'telemetria.db' e índices inicializados correctamente.")

def al_conectar(cliente, userdata, flags, rc, propiedades=None):
    """Suscripción a topics jerárquicos usando el comodín +."""
    print(f"[{datetime.now().isoformat()}] Suscriptor conectado al broker (rc={rc})")
    cliente.subscribe("flota/+/gps")
    cliente.subscribe("flota/+/temperatura")
    cliente.subscribe("flota/+/combustible")
    print("Suscrito exitosamente a: flota/+/gps, flota/+/temperatura, flota/+/combustible")

def al_recibir_mensaje(cliente, userdata, mensaje):
    """Procesa e inserta los datos recibidos y evalúa reglas de alerta."""
    topic = mensaje.topic
    payload = json.loads(mensaje.payload.decode('utf-8'))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # --- Guardar GPS ---
    if "/gps" in topic:
        cursor.execute('''
            INSERT INTO gps_data (vehicle_id, lat, lng, speed, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            payload["vehicle_id"],
            payload["lat"],
            payload["lng"],
            payload["speed"],
            payload["timestamp"]
        ))
        
    # --- Guardar y evaluar Temperatura ---
    elif "/temperatura" in topic:
        temp = payload.get("temperature", 0)
        vehicle_id = payload.get("vehicle_id")
        
        # Regla de alerta: Temperatura > 4 °C
        if temp > 4:
            print(f"⚠️  [ALERTA TEMPERATURA] Vehículo: {vehicle_id} | Valor: {temp} °C (Supera los 4 °C)")
            
        cursor.execute('''
            INSERT INTO temp_data (vehicle_id, temperature, unit, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            vehicle_id,
            temp,
            payload.get("unit", "celsius"),
            payload.get("timestamp")
        ))
        
    # --- Guardar y evaluar Combustible ---
    elif "/combustible" in topic:
        fuel = payload.get("fuel_level", 0)
        vehicle_id = payload.get("vehicle_id")
        
        # Regla de alerta: Combustible < 20 %
        if fuel < 20:
            print(f"⚠️  [ALERTA COMBUSTIBLE] Vehículo: {vehicle_id} | Nivel: {fuel} % (Menor al 20 %)")
            
        cursor.execute('''
            INSERT INTO fuel_data (vehicle_id, fuel_level, unit, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (
            vehicle_id,
            fuel,
            payload.get("unit", "percent"),
            payload.get("timestamp")
        ))
        
    conn.commit()
    conn.close()

def principal():
    inicializar_base_datos()
    
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_connect = al_conectar
    cliente.on_message = al_recibir_mensaje
    
    cliente.connect(BROKER, PORT, 60)
    print("Iniciando servicio de almacenamiento SQLite...")
    
    try:
        cliente.loop_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo suscriptor...")
        cliente.disconnect()

if __name__ == "__main__":
    principal()