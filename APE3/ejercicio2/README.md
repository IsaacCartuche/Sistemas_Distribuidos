# APE 3 - Ejercicio 2: Cajero Automático Compartido (Exclusión Mutua)

## Objetivo
Implementar exclusión mutua para evitar condiciones de carrera sobre un recurso compartido (saldo bancario).

---

## Situación
- Cuenta con **saldo inicial $1000**
- **3 procesos concurrentes**:
  - Proceso 1: retiro $300
  - Proceso 2: retiro $250
  - Proceso 3: depósito $200
- Saldo debe modificarse de forma segura

---

## Solución implementada

### Backend (Spring Boot)
- **Tecnología**: Java 17, Spring Boot, Maven
- **Sincronización**: `java.util.concurrent.locks.ReentrantLock` (mutex)
- **Endpoints**:
  - `GET /api/cajero/simular` — Ejecuta los 3 hilos concurrentes y retorna logs + saldo final

### Frontend (HTML/JS + Nginx)
- Interfaz simple para disparar simulación y ver logs
- Puerto: **3000** (mapeado a 80 en contenedor)

---

## Estructura
```
ejercicio2/
├── docker-compose.yml
├── backend-cajero/
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/main/java/com/practica/cajero/
│       ├── controller/CajeroController.java
│       └── service/CuentaBancariaService.java    # ReentrantLock + ExecutorService
└── frontend-cajero/
    ├── Dockerfile (nginx:alpine)
    ├── index.html
    ├── app.js
    └── style.css
```

---

## Despliegue

```bash
cd /home/isaac/Documents/Sistemas_Distribuidos/APE3/ejercicio2
docker compose up --build
```

**Acceso:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080/api/cajero/simular

---

## Verificación (Criterio guía)
> **Saldo final = $650** — Ejecutar varias veces y comprobar que el saldo no varíe

```
$1000 - $300 - $250 + $200 = $650
```

El `ReentrantLock` garantiza que las operaciones `retirar` y `depositar` son atómicas.

---

## Pseudocódigo (guía)
```
saldo = 1000
MUTEX mutex_saldo = 1

PROCEDIMIENTO retirar(id, cantidad)
    lock(mutex_saldo)
    SI saldo >= cantidad ENTONCES
        saldo = saldo - cantidad
    FIN SI
    unlock(mutex_saldo)
FIN PROCEDIMIENTO

PROCEDIMIENTO depositar(id, cantidad)
    lock(mutex_saldo)
    saldo = saldo + cantidad
    unlock(mutex_saldo)
FIN PROCEDIMIENTO
```

---

## Pregunta de análisis
> ¿Por qué el acceso a saldo debe protegerse con un mutex?
Sin mutex, dos hilos pueden leer `saldo` simultáneamente, ambos ver $1000, ambos restar sus cantidades, y escribir un resultado incorrecto (condición de carrera). El mutex serializa el acceso: check + update atómico.