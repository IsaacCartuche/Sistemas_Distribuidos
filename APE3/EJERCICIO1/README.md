# APE 3 - Ejercicio 1: Control de Acceso a Estacionamiento (Semáforo Contador)

## Objetivo
Aplicar semáforos contadores para controlar el acceso concurrente a un recurso limitado (4 espacios de estacionamiento) con 10 vehículos concurrentes.

---

## Situación
- Estacionamiento con **4 espacios**
- **10 vehículos** llegan concurrentemente
- Cada vehículo espera si no hay espacio disponible
- Al salir, libera el espacio para otro vehículo

---

## Solución implementada

### Backend (Spring Boot)
- **Tecnología**: Java 17, Spring Boot, Maven
- **Sincronización**: `java.util.concurrent.Semaphore(4, true)` — fair FIFO
- **Endpoints**:
  - `POST /api/estacionamiento/ingresar/{id}?tiempoMs=3000` — Simula vehículo entrando, estacionando y saliendo
  - `GET /api/estacionamiento/estado` — Espacios disponibles / capacidad total

### Frontend (React + Vite + Nginx)
- Interfaz para lanzar vehículos y ver estado en tiempo real
- Puerto: **3001** (mapeado a 80 en contenedor)

---

## Estructura
```
EJERCICIO1/
├── docker-compose.yml
├── estacionamiento-backend/
│   ├── Dockerfile (multi-stage: builder + jre-alpine)
│   ├── pom.xml
│   └── src/main/java/com/sistemas/distribuidos/estacionamiento/
│       ├── controller/EstacionamientoController.java
│       ├── service/EstacionamientoService.java     # Semaphore(4) fair
│       └── dto/PaqueteVehiculoDto.java
└── estacionamiento-frontend/
    ├── Dockerfile (nginx:alpine)
    ├── nginx.conf
    ├── index.html + src/ (React)
    └── package.json
```

---

## Despliegue

```bash
cd /home/isaac/Documents/Sistemas_Distribuidos/APE3/EJERCICIO1
docker compose up --build
```

**Acceso:**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8080/api/estacionamiento/estado

---

## Verificación (Criterio guía)
> **Vehículos dentro ≤ 4** — Verificar que nunca ingresen más de 4 simultáneamente

El semáforo `fair=true` garantiza FIFO y evita inanición.

---

## Pseudocódigo (guía)
```
SEMÁFORO espacios = 4

PROCEDIMIENTO vehiculo(id)
    escribir("Vehículo ", id, " llega al estacionamiento")
    wait(espacios)
    escribir("Vehículo ", id, " ingresa al estacionamiento")
    estacionar(id)
    esperar_tiempo()
    escribir("Vehículo ", id, " sale del estacionamiento")
    signal(espacios)
FIN PROCEDIMIENTO
```

---

## Pregunta de análisis
> ¿Qué ocurriría si el semáforo se inicializara en 1? ¿Y si se inicializara en 10?
- **1**: Solo 1 vehículo a la vez (exclusión mutua, no aprovecha los 4 espacios)
- **10**: Caben los 10 vehículos a la vez (excede capacidad real = 4)