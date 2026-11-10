# APE 3 - Ejercicio 3: Fábrica de Ensamblaje — Productor-Consumidor

## Objetivo
Implementar el patrón productor-consumidor utilizando una cola limitada y semáforos.

---

## Situación
- Línea de producción con **capacidad 5 piezas**
- **Productores** fabrican piezas
- **Consumidores** toman piezas para ensamblar
- Productor no puede colocar si almacén lleno
- Consumidor no puede retirar si almacén vacío

---

## Solución implementada

### Backend (3 microservicios Spring Boot)
| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `almacen-service` | 8080 | Buffer compartido (Monitor): `Semaphore(espacios=5)`, `Semaphore(elementos=0)`, `ReentrantLock` |
| `productor-service` | 8081 | Llama `POST /almacen/producir` repetidamente |
| `consumidor-service` | 8082 | Llama `GET /almacen/consumir` repetidamente |

### Frontend (Nginx estático)
- Puerto: **5500** (mapeado a 80)
- Visualiza estado del buffer en tiempo real

---

## Estructura
```
EJERCICIO3/
├── docker-compose.yml
└── backend-productor-consumidor/
    ├── almacen-service/
    │   ├── Dockerfile
    │   ├── pom.xml
    │   └── src/main/java/ec/unl/distribuidos/almacen/
    │       ├── BufferAcotado.java          # Monitor: Semaphore + Mutex + Deque
    │       └── AlmacenController.java      # REST: /producir, /consumir, /estado
    ├── productor-service/
    │   ├── Dockerfile
    │   └── src/main/java/.../productor/    # Cliente HTTP → almacen
    └── consumidor-service/
        ├── Dockerfile
        └── src/main/java/.../consumidor/   # Cliente HTTP → almacen
```

---

## Despliegue

```bash
cd /home/isaac/Documents/Sistemas_Distribuidos/APE3/EJERCICIO3
docker compose up --build
```

**Acceso:**
- Frontend: http://localhost:5500
- Almacen API: http://localhost:8080/almacen/estado
- Productor: http://localhost:8081
- Consumidor: http://localhost:8082

---

## Verificación (Criterio guía)
> **Todos los productos producidos son consumidos** — Verificar que el almacén nunca supere 5 ni quede con inconsistencias

El monitor `BufferAcotado` garantiza:
- `espacios.acquire()` → bloquea si buffer lleno
- `elementos.acquire()` → bloquea si buffer vacío
- `mutex` protege la `Deque` en inserción/extracción

---

## Pseudocódigo (guía)
```
COLA almacen CAPACIDAD = 5
SEMÁFORO espacios = 5
SEMÁFORO elementos = 0
MUTEX mutex_almacen = 1

PROCEDIMIENTO productor(id)
    REPETIR 5 VECES
        pieza = fabricar_pieza()
        wait(espacios)
        lock(mutex_almacen)
        insertar(almacen, pieza)
        unlock(mutex_almacen)
        signal(elementos)
    FIN REPETIR
FIN PROCEDIMIENTO

PROCEDIMIENTO consumidor(id)
    REPETIR 5 VECES
        wait(elementos)
        lock(mutex_almacen)
        pieza = extraer(almacen)
        unlock(mutex_almacen)
        signal(espacios)
        ensamblar(pieza)
    FIN REPETIR
FIN PROCEDIMIENTO
```

---

## Pregunta de análisis
> ¿Qué sucede si `espacios` se inicializa en 0? ¿Qué sucede si `elementos` se inicializa en 5?
- **espacios=0**: Productores bloqueados inmediatamente (buffer "lleno" desde inicio) — deadlock
- **elementos=5**: Consumidores creen que hay 5 piezas falsas → extraen de buffer vacío → error/inconsistencia