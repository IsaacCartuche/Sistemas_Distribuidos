# APE 6 — Sistema Integral de Monitoreo de Flota (IoT + Microservicios)

## Objetivo
Sistema completo de monitoreo de flota logística integrando:
- **Capa IoT (Python + MQTT)**: Simulador sensores → Mosquitto → Suscriptor SQLite + Puente RabbitMQ
- **Capa Microservicios (Spring Boot + AMQP)**: Consumidores RabbitMQ → H2/JPA → REST API
- **Infraestructura**: Mosquitto (MQTT) + RabbitMQ (AMQP) con Docker Compose

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RED HOST (network_mode: host)                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    MQTT/1883    ┌──────────────┐    AMQP/5672    ┌──────┐ │
│  │  Simulador   │ ──────────────► │  Mosquitto   │ ◄─────────────► │Bridge│ │
│  │  (Python)    │  flota/{id}/    │  (Broker)    │                 │(Py)  │ │
│  └──────────────┘   gps/temp/     └──────┬───────┘                 └──┬───┘ │
│                                           │                            │     │
│                      ┌────────────────────┘                            │     │
│                      ▼                                                 │     │
│  ┌──────────────┐    MQTT/1883    ┌──────────────────┐                │     │
│  │  Suscriptor  │ ◄────────────── │   Mosquitto      │                │     │
│  │  SQLite (Py) │  flota/+/...    │                  │                │     │
│  └──────────────┘                 └──────────────────┘                │     │
│                                                                             │
│                                                                       ┌────▼────┐ │
│                                                                       │RabbitMQ │ │
│                                                                       │(Mgmt)   │ │
│                                                                       └────┬────┘ │
│                                                                            │     │
│  ┌──────────────────────────────────────────────────────────────────────▼──┐ │
│  │                    Spring Boot: fleet-monitor                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │ │
│  │  │ GpsConsumer │  │AlertConsumer│  │GpsRepository│  │FleetController│  │
│  │  │cola.gps...  │  │cola.alertas.│  │   H2/JPA    │  │  REST API     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura del proyecto

```
APE6/
├── docker-compose.yml              # Orquestación completa (host network)
├── infra/
│   ├── docker-compose.yml          # Solo infra: Mosquitto + RabbitMQ
│   └── mosquitto/
│       ├── config/mosquitto.conf   # listener 1883, persistence
│       └── data/                   # mosquitto.db persistido
└── services/
    ├── python/                     # Capa IoT (Python)
    │   ├── bridge.py               # Puente MQTT → RabbitMQ (4 colas)
    │   ├── simulador_sensores.py   # 3 vehículos × 3 sensores, QoS 1
    │   ├── suscriptor_almacenamiento.py  # SQLite + alertas
    │   ├── requirements.txt        # paho-mqtt, pika
    │   ├── Dockerfile.bridge
    │   └── Dockerfile.simulador
    └── spring-boot/
        └── fleet-monitor/          # Microservicio Spring Boot
            ├── Dockerfile          # Multi-stage Maven + JRE
            ├── pom.xml             # Spring Boot 3.1.5, AMQP, JPA, H2, Web
            └── src/main/java/com/fleet/monitor/
                ├── config/RabbitMQConfig.java    # DirectExchange + 4 colas + bindings
                ├── consumer/GpsConsumer.java     # @RabbitListener(cola.gps.telemetria) → H2
                ├── consumer/AlertConsumer.java   # @RabbitListener(alertas) → notificaciones
                ├── model/GpsMessage.java         # DTO JSON (vehicle_id, lat, lng, speed, timestamp)
                ├── model/GpsEntity.java          # JPA Entity → H2 table gps_data
                ├── repository/GpsRepository.java # JPA + custom queries
                └── controller/FleetController.java  # REST /api/fleet/status, /vehicle/{id}/telemetria
```

---

## Servicios y Puertos

| Servicio | Contenedor | Puerto | Descripción |
|----------|------------|--------|-------------|
| Mosquitto | `mosquitto_broker` | 1883 (MQTT), 9001 (WS) | Broker MQTT IoT |
| RabbitMQ | `rabbitmq_broker` | 5672 (AMQP), 15672 (UI) | Broker empresarial + Management |
| Bridge | `mqtt_rabbitmq_bridge` | — | Python: MQTT `flota/#` → RabbitMQ 4 colas |
| Simulador | `simulador_sensores` | — | Python: 3 vehículos × 3 sensores c/5s |
| Fleet Monitor | `fleet_monitor` | 8080 | Spring Boot REST + Consumers RabbitMQ |

**Credenciales RabbitMQ:** `admin` / `admin123` (definidas en docker-compose.yml)

---

## Colas RabbitMQ (declaradas en bridge.py + RabbitMQConfig.java)

| Cola | Origen | Destino | Patrón |
|------|--------|---------|--------|
| `cola.gps.telemetria` | Bridge (todos GPS) | GpsConsumer → H2 | Point-to-point |
| `cola.alertas.temperatura` | Bridge (temp > 4°C) | AlertConsumer → notificaciones | Pub/Sub via exchange |
| `cola.combustible.nivel` | Bridge (fuel < 20%) | AlertConsumer → notificaciones | Pub/Sub via exchange |
| `cola.notificaciones` | AlertConsumer (re-envío) | Futuro consumidor | Competing consumers |

**Exchange:** `exchange.fleet` (Direct) con routing keys: `gps.routing`, `temp.alert`, `fuel.routing`

---

## Despliegue completo

```bash
cd ~/APE6

# Levantar toda la pila (infra + servicios)
docker compose up --build -d

# Verificar estado
docker compose ps
# NAME                  STATUS              PORTS
# mosquitto_broker      Up                  1883, 9001
# rabbitmq_broker       Up                  5672, 15672
# mqtt_rabbitmq_bridge  Up                  (host network)
# simulador_sensores    Up                  (host network)
# fleet_monitor         Up                  8080

# Ver logs
docker compose logs -f simulador_sensores
docker compose logs -f mqtt_rabbitmq_bridge
docker compose logs -f fleet_monitor

# RabbitMQ Management UI
# http://localhost:15672  (admin / admin123)
```

---

## Verificación funcional

### 1. Simulador publicando (logs)
```
[2026-11-10T...] 3 sensores publicados para VH-001
[2026-11-10T...] 3 sensores publicados para VH-002
--- Ronda completada (9 mensajes enviados) ---
```

### 2. Puente enrutando a RabbitMQ
```
[RABBITMQ] GPS enviado
⚠️ [RABBITMQ] Alerta Temp enviada
⚠️ [RABBITMQ] Alerta Combustible enviada
```

### 3. Consumidores Spring Boot
```
GPS guardado: VH-001
ALERTA TEMPERATURA: {...}
ALERTA COMBUSTIBLE: {...}
```

### 4. REST API Fleet Monitor
```bash
# Estado flota
curl http://localhost:8080/api/fleet/status
# {"totalVehicles": 3, "activeAlerts": 0, "timestamp": "..."}

# Telemetría vehículo
curl http://localhost:8080/api/fleet/vehicle/VH-001/telemetria
# [{"vehicleId":"VH-001","lat":-2.1701,"lng":-79.921,"speed":45.2,"timestamp":"..."}, ...]
```

### 5. Verificar colas RabbitMQ
```bash
docker exec rabbitmq_broker rabbitmqadmin list queues name messages
# cola.gps.telemetria     15
# cola.alertas.temperatura 3
# cola.combustible.nivel   2
# cola.notificaciones      5
```

---

## Base de datos

| Capa | Motor | Tablas/Entidades |
|------|-------|------------------|
| Python (Suscriptor) | SQLite (`telemetria.db`) | `gps_data`, `temp_data`, `fuel_data` |
| Spring Boot (Fleet Monitor) | H2 (embebido) | `gps_data` (JPA Entity) |

---

## Diferencias con APE 5

| Aspecto | APE 5 (Parte 1) | APE 6 (Integral) |
|---------|-----------------|------------------|
| **Alcance** | Solo capa IoT (Python) | IoT + Microservicios Spring Boot |
| **Puente** | 3 colas (GPS, temp, fuel) | **4 colas** (+ notificaciones) |
| **Consumo RabbitMQ** | No | **Sí: GpsConsumer + AlertConsumer** |
| **Persistencia alertas** | Solo consola | **Re-envío a `cola.notificaciones`** |
| **API REST** | No | **Sí: `/api/fleet/status`, `/vehicle/{id}/telemetria`** |
| **BD microservicios** | No | **H2 + JPA** |
| **Exchange RabbitMQ** | No (direct queues) | **DirectExchange `exchange.fleet` + bindings** |
| **Red** | Bridge (puertos mapeados) | **Host network** (localhost entre contenedores) |

---

## Archivos Dockerfile

```dockerfile
# services/python/Dockerfile.simulador
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY simulador_sensores.py .
CMD ["python", "simulador_sensores.py"]

# services/python/Dockerfile.bridge
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bridge.py .
CMD ["python", "bridge.py"]

# services/spring-boot/fleet-monitor/Dockerfile (multi-stage)
FROM maven:3.9.6-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn -B dependency:go-offline -DskipTests
COPY src ./src
RUN mvn -B clean package -DskipTests
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

---

## Estado: ✅ COMPLETO

| Componente | Implementado | Verificado |
|------------|--------------|------------|
| Mosquitto + RabbitMQ (Docker) | ✅ | `docker compose up` |
| Simulador sensores (Python, QoS 1) | ✅ | Logs 9 msg/ronda |
| Suscriptor SQLite + alertas | ✅ | `telemetria.db` 3 tablas |
| Puente MQTT→RabbitMQ (4 colas) | ✅ | Colas con mensajes |
| Spring Boot Fleet Monitor | ✅ | Compila, REST en 8080 |
| GpsConsumer → H2 | ✅ | JPA save |
| AlertConsumer → notificaciones | ✅ | RabbitTemplate send |
| REST API (`/api/fleet/*`) | ✅ | JSON response |
| RabbitMQ Exchange + Bindings | ✅ | `exchange.fleet` Direct |
| Documentación (README) | ✅ | Este archivo |

---
