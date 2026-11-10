# APE 5 — Mensajería Distribuida con RabbitMQ y MQTT

## Objetivo (según guía)
Implementar la capa IoT de un sistema de monitoreo de flota logística utilizando:
- **MQTT** (Mosquitto broker) para sensores vehiculares
- **SQLite** para almacenamiento de telemetría con alertas automáticas
- **RabbitMQ** (AMQP) para procesamiento de alertas vía servicio puente
- **Patrones**: pub/sub (MQTT), routing + competing consumers (RabbitMQ)

---

## Arquitectura

```
┌─────────────────┐     MQTT (1883)      ┌──────────────────┐
│  Simulador      │  flota/{vehiculo}/   │   Suscriptor     │
│  Sensores IoT   │  gps                 │   SQLite +       │
│  (3 vehículos)  │  temperatura         │   Alertas        │
│                 │  combustible         └────────┬─────────┘
└─────────────────┘                              │
                                                 │ MQTT (flota/#)
                                                 ▼
┌─────────────────┐     AMQP (5672)      ┌──────────────────┐
│  RabbitMQ       │  cola.gps.telemetria │   Microservicios │
│  (Management)   │  cola.alertas.*      │   (futuro)       │
└─────────────────┘                      └──────────────────┘
```

**Tópicos MQTT jerárquicos:** `flota/{VH-001,VH-002,VH-003}/{gps,temperatura,combustible}`

---

## Estructura del proyecto

```
APE5/
├── docker-compose.yml          # Mosquitto + RabbitMQ
├── requirements.txt            # paho-mqtt, pika
├── mosquitto/
│   ├── config/mosquitto.conf   # listener 1883, persistence
│   └── data/                   # mosquitto.db (persistido)
├── sensor_simulador.py         # Publicador: 3 vehículos × 3 sensores (QoS 1)
├── simulador_sensores.py       # Versión alternativa (9 msg/ronda)
├── suscriptor_almacenamiento.py # Suscriptor básico (alertas en consola)
├── suscriptor_sqlite.py        # Suscriptor completo: SQLite + alertas + índices
├── mqtt_rabbitmq_bridge.py     # Puente: MQTT → RabbitMQ (filtra alertas)
├── telemetria.db               # Base de datos SQLite (3 tablas)
└── README.md                   # Este archivo
```

---

## Requisitos
- Docker + Docker Compose
- Python 3.10+ con `paho-mqtt>=2.0.0`, `pika>=1.3.0`

---

## Despliegue

```bash
cd ~/APE5

# 1. Levantar brokers
docker compose up -d

# Verificar
docker compose ps
# NAME                IMAGE                       PORTS
# mosquitto_broker    eclipse-mosquitto:2.0       1883, 9001
# rabbitmq_broker     rabbitmq:3-management       5672, 15672

# 2. Ejecutar simulador de sensores (Terminal 1)
python sensor_simulador.py

# 3. Ejecutar suscriptor con almacenamiento (Terminal 2)
python suscriptor_sqlite.py

# 4. Ejecutar puente MQTT-RabbitMQ (Terminal 3)
python mqtt_rabbitmq_bridge.py
```

**RabbitMQ Management UI:** http://localhost:15672 (guest/guest)

---

## Verificación funcional (Resultados esperados)

| Componente | Criterio guía | Verificación |
|------------|---------------|--------------|
| **Broker MQTT** | Mosquitto en Docker, recibe/distribuye mensajes | `docker logs mosquitto_broker` muestra conexiones |
| **Simulador IoT** | 3 vehículos, GPS + temp + combustible, topics jerárquicos | `sensor_simulador.py` publica cada 5s |
| **Suscriptor SQLite** | Almacena en 3 tablas, alertas temp > 4°C, fuel < 20% | `telemetria.db` con 420+ registros |
| **Puente MQTT-RabbitMQ** | Filtra alertas → colas durables | `cola.gps.telemetria`, `cola.alertas.temperatura`, `cola.combustible.nivel` |

**Probar colas RabbitMQ:**
```bash
python -c "
import pika
cred = pika.PlainCredentials('guest','guest')
conn = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=cred))
ch = conn.channel()
for q in ['cola.gps.telemetria','cola.alertas.temperatura','cola.combustible.nivel']:
    m = ch.queue_declare(queue=q, passive=True)
    print(f'{q}: {m.method.message_count} msgs')
conn.close()
"
```

---

## Archivos clave

| Archivo | Función | Cumple guía |
|---------|---------|-------------|
| `docker-compose.yml` | Mosquitto (1883/9001) + RabbitMQ (5672/15672) | ✅ Actividad 1 |
| `sensor_simulador.py` | 3 vehículos, QoS 1, topics `flota/{id}/{sensor}` | ✅ Actividad 2 |
| `suscriptor_sqlite.py` | 3 tablas, alertas temp>4°C/fuel<20%, wildcards `flota/+/...` | ✅ Actividad 3 |
| `mqtt_rabbitmq_bridge.py` | Suscribe `flota/#`, 3 colas durables, `delivery_mode=2` | ✅ Actividad 4 |
| `mosquitto/config/mosquitto.conf` | `listener 1883 allow_anonymous true persistence` | ✅ Config |

---

## Preguntas de control (guía Sección 6)

1. **Diferencias MQTT vs AMQP**: MQTT = ligero, pub/sub, topics jerárquicos, QoS 0/1/2, ideal IoT (bajo ancho de banda). AMQP = empresarial, exchanges/colas/bindings/routing keys, patrones point-to-point/pub/sub/routing, persistencia, ACKs, management UI.

2. **Topics vs Exchanges/Colas**: MQTT topics = filtrado por suscripción con wildcards (`+`, `#`), simple, escalable para millones de dispositivos. RabbitMQ exchanges + bindings = routing flexible, múltiples patrones, control fino, durabilidad, TTL, DLX.

3. **QoS en MQTT**:
   - **QoS 0** (como máx. 1 vez): sin ACK, menor latencia, posible pérdida. *Uso: telemetría GPS frecuente donde pérdida ocasional es tolerable.*
   - **QoS 1** (al menos 1 vez): PUBACK, retransmisión si no hay ACK. *Uso: alertas de temperatura/combustible (guía usa QoS 1).*
   - **QoS 2** (exactamente 1 vez): handshake 4 pasos (PUBREC/PUBREL/PUBCOMP). *Uso: comandos críticos (ej. frenado de emergencia), no telemetría.*

---

## Notas de implementación

- **QoS 1** en `sensor_simulador.py` (`client.publish(..., qos=1)`) — cumple guía
- **Colas durables** + `delivery_mode=2` en bridge — mensajes persistentes en RabbitMQ
- **Wildcards MQTT**: `flota/+/gps` (un nivel), `flota/#` (multi-nivel en bridge)
- **Base de datos**: 3 tablas separadas (`gps_data`, `temp_data`, `fuel_data`) con índices implícitos en PK
- **Alertas**: Impresión en consola + enriquecimiento en RabbitMQ (`tipo_alerta`, `mensaje`)

---

## Estado: COMPLETO

Todos los entregables de la **Parte 1 (Capa IoT)** implementados y funcionales:
- Broker MQTT (Mosquitto Docker)
- Simulador sensores (3 vehículos × 3 sensores)
- Suscriptor + SQLite + alertas
- Puente MQTT → RabbitMQ (3 colas, filtrado alertas)
- Documentación

> **Nota:** Este avance cumple únicamente la parte 1 del proyecto, la parte 2 corresponde al APE 6.