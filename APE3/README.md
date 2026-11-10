# APE 3 — Sincronización de Procesos: Exclusión Mutua, Semáforos y Problemas Clásicos de Concurrencia

## Objetivo (según guía)
Implementar mecanismos de sincronización para resolver problemas clásicos de concurrencia:
1. **Exclusión mutua** (mutex/locks) — proteger secciones críticas
2. **Semáforos contadores** — controlar acceso a recursos limitados
3. **Productor-Consumidor** — buffer compartido con semáforos
4. **Lectores-Escritores / Cruce direccional** — coordinación de acceso incompatible
5. **Sincronización por etapas** — orden fijo de ejecución (Diseño → Revisión → Impresión)

---

## Estructura del proyecto

```
APE3/
├── EJERCICIO1/                    # Estacionamiento — Semáforo contador (4 espacios, 10 vehículos)
│   ├── docker-compose.yml
│   ├── estacionamiento-backend/   # Spring Boot + Semaphore(4)
│   └── estacionamiento-frontend/  # React/Vite + Nginx
├── ejercicio2/                    # Cajero automático — Exclusión mutua (Mutex/ReentrantLock)
│   ├── docker-compose.yml
│   ├── backend-cajero/            # Spring Boot + ReentrantLock
│   └── frontend-cajero/           # HTML/JS estático + Nginx
├── EJERCICIO3/                    # Productor-Consumidor — Buffer acotado (capacidad 5)
│   ├── docker-compose.yml
│   ├── backend-productor-consumidor/
│   │   ├── almacen-service/       # Spring Boot: BufferAcotado (Semaphore + Mutex)
│   │   ├── productor-service/     # Spring Boot: produce piezas
│   │   └── consumidor-service/    # Spring Boot: consume piezas
│   └── frontend-productor-consumidor/  # HTML estático + Nginx
├── Ejercicio4/                    # Cruce de vehículos — Control direccional (Mutex + Condition)
│   ├── docker-compose.yml
│   ├── puente-backend/            # Spring Boot: PuenteService (ReentrantLock fair + Condition)
│   ├── puente-frontend/           # React + Nginx
│   └── README.md                  # Documentación completa existente
├── ejercicio5/                    # Centro de impresión — Sincronización por etapas (3 semáforos)
│   ├── docker-compose.yml
│   ├── backend-impresion/         # Spring Boot: 3 Semaphores (turno_diseño=1, revisión=0, impresión=0)
│   └── frontend-impresion/        # HTML/JS estático + Nginx
└── README.md                      # Este archivo
```

---

## Ejercicios y criterios de verificación (según guía)

| Ejercicio | Problema | Mecanismo | Criterio de verificación |
|-----------|----------|-----------|--------------------------|
| **1. Estacionamiento** | 4 espacios, 10 vehículos concurrentes | `Semaphore(4)` | Nunca >4 vehículos simultáneos |
| **2. Cajero** | Saldo $1000, 3 hilos (retiro 300, retiro 250, depósito 200) | `ReentrantLock` (mutex) | Saldo final siempre $650 |
| **3. Productor-Consumidor** | Buffer capacidad 5, 2 productores, 2 consumidores | `Semaphore(espacios=5, elementos=0)` + `Mutex` | Buffer nunca >5 ni <0; todas las piezas consumidas |
| **4. Puente** | Un carril, dirección única activa, anti-inanición | `ReentrantLock(fair)` + `Condition` | Nunca vehículos N y S simultáneos; fairness por lotes |
| **5. Impresión** | 3 etapas secuenciales: Diseño → Revisión → Impresión ×3 docs | 3 `Semaphore` (1,0,0) | Orden estricto D→R→I por documento |

---

## Preguntas de control (guía - Sección 7)

1. ¿Qué es una condición de carrera?
2. Diferencia fundamental entre semáforo binario y mutex. ¿Pueden usarse indistintamente? (mín. 2 diferencias prácticas)
3. ¿Qué es un interbloqueo (deadlock) y las 4 condiciones de Coffman? ¿Cuál elimina el ordenamiento de recursos?

---

## Despliegue general

Cada ejercicio tiene su propio `docker-compose.yml` independiente:

```bash
# Ejercicio 1: Estacionamiento
cd ~/APE3/EJERCICIO1 && docker compose up --build

# Ejercicio 2: Cajero
cd ~/APE3/ejercicio2 && docker compose up --build

# Ejercicio 3: Productor-Consumidor
cd ~/APE3/EJERCICIO3 && docker compose up --build

# Ejercicio 4: Puente
cd ~/APE3/Ejercicio4 && docker compose up --build

# Ejercicio 5: Impresión
cd ~/APE3/ejercicio5 && docker compose up --build
```

**Puertos típicos:**
- Backend: 8080 (o 8081 para ejercicio 5)
- Frontend: 3000, 3001, 5500 según ejercicio

---

## Estado de implementación

| Ejercicio | Backend (Spring Boot) | Frontend | Docker Compose |
|-----------|----------------------|----------|----------------|
| 1. Estacionamiento | ✅ `Semaphore(4)` fair | ✅ React/Vite | ✅ |
| 2. Cajero | ✅ `ReentrantLock` | ✅ HTML/JS | ✅ |
| 3. Productor-Consumidor | ✅ BufferAcotado (Sem+Mutex) | ✅ HTML | ✅ |
| 4. Puente | ✅ `ReentrantLock` + `Condition` + fairness | ✅ React | ✅ |
| 5. Impresión | ✅ 3 Semáforos (1,0,0) | ✅ HTML/JS | ✅ |

