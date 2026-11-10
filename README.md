# Sistemas Distribuidos — Repositorio de Prácticas (APE 1-6)

## Materia
Sistemas Distribuidos — 6to Ciclo — Carrera de Computación — FEIRNNR / Universidad Nacional de Loja

## Propósito del repositorio
Contiene las 6 Actividades Práctico-Experimentales (APE) del curso, cada una implementando conceptos fundamentales de sistemas distribuidos con código funcional y dockerizado para ejecución local.

## Contenido por APE

| APE | Tema | Tecnologías principales | Estado |
|-----|------|------------------------|--------|
| **APE 1** | Análisis colaborativo de arquitecturas (Cliente-Servidor, P2P, Multicapa, Microservicios) | Documentación, Diagramas draw.io | Documentación completa |
| **APE 2** | Arquitectura Cliente-Servidor con comunicación por archivos | Python, Docker, docker-compose | Dockerizado, funcional |
| **APE 3** | Sincronización: Exclusión mutua, Semáforos, Productor-Consumidor, Puente, Impresión | Spring Boot (5 ejercicios independientes), Maven, Docker | 5 microservicios dockerizados |
| **APE 4** | IPC + Sockets TCP + IA (Ollama) — Sistema de asignación de pedidos | Python, multiprocessing, socket, Ollama | Código base, pendiente dockerizar |
| **APE 5** | Capa IoT: MQTT (Mosquitto) + RabbitMQ — Sensores, SQLite, Puente | Python (paho-mqtt, pika), Mosquitto, RabbitMQ, SQLite | Dockerizado, funcional |
| **APE 6** | Sistema integral IoT + Microservicios Spring Boot | Spring Boot (AMQP, JPA, H2, Web), Python, Mosquitto, RabbitMQ | Dockerizado, funcional |

## Estructura general

```
Sistemas_Distribuidos/
├── APE 1/              # Documentación y diagramas
├── APE2/               # Cliente-Servidor archivos (Python + Docker)
├── APE3/               # 5 ejercicios sincronización (Spring Boot)
├── APE4/ape/           # IPC + TCP + IA (Python, Ollama)
├── APE5/               # MQTT + RabbitMQ (Python, Docker)
├── APE6/               # IoT + Microservicios (Spring Boot + Python + Docker)
└── Clase_Invertida_Sockets_Ejercicio/
```

## Requisitos globales

- Docker + Docker Compose
- Python 3.10+ (para APE 2, 4, 5, 6)
- Java 17 + Maven (para APE 3, 6)
- Ollama instalado localmente (para APE 4)

## Ejecución rápida

Cada APE tiene su propio `docker-compose.yml` independiente:

```bash
# APE 2
cd APE2/APE2 && docker compose up --build

# APE 3 (cada ejercicio por separado)
cd APE3/EJERCICIO1 && docker compose up --build
cd APE3/ejercicio2 && docker compose up --build
# ...

# APE 5
cd APE5 && docker compose up -d
python sensor_simulador.py    # Terminal 1
python suscriptor_sqlite.py   # Terminal 2
python mqtt_rabbitmq_bridge.py # Terminal 3

# APE 6
cd APE6 && docker compose up -d
# REST API: http://localhost:8081/api/fleet/status
# RabbitMQ UI: http://localhost:15674 (admin/admin123)
```

## Puertos por APE (evitan conflictos)

| APE | Mosquitto | RabbitMQ AMQP | RabbitMQ UI | Otros |
|-----|-----------|---------------|-------------|-------|
| APE 5 | 1884 / 9002 | 5673 | 15673 | — |
| APE 6 | 1885 / 9003 | 5674 | 15674 | Fleet Monitor 8081, Bridge 8082 |