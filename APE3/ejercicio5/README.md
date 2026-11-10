# APE 3 - Ejercicio 5: Centro de Impresión (Sincronización por Etapas)

## Objetivo
Utilizar semáforos para establecer un orden determinado de ejecución entre procesos: **Diseño → Revisión → Impresión**.

---

## Situación
Tres procesos que deben ejecutarse en orden estricto para cada documento:
1. **Diseño** — prepara el documento
2. **Revisión** — verifica el documento (solo después de Diseño)
3. **Impresión** — imprime el documento (solo después de Revisión)

Ciclo se repite para **3 documentos**.

---

## Solución implementada

### Backend (Spring Boot)
- **Tecnología**: Java 17, Spring Boot, Maven
- **Sincronización**: 3 `Semaphore`
  - `turnoDiseno = 1` (inicia)
  - `turnoRevision = 0`
  - `turnoImpresion = 0`
- **Endpoints**:
  - `GET /api/impresion/simular` — Ejecuta 3 hilos (uno por etapa) × 3 documentos

### Frontend (HTML/JS + Nginx)
- Dispara simulación y muestra logs ordenados
- Puerto: **3001** (mapeado a 80 en contenedor)

---

## Estructura
```
ejercicio5/
├── docker-compose.yml
├── backend-impresion/
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/main/java/com/practica/impresion/
│       ├── controller/ImpresionController.java
│       └── service/CentroImpresionService.java    # 3 Semaphores + ExecutorService
└── frontend-impresion/
    ├── Dockerfile (nginx:alpine)
    ├── index.html
    ├── app.js
    └── style.css
```

---

## Despliegue

```bash
cd /home/isaac/Documents/Sistemas_Distribuidos/APE3/ejercicio5
docker compose up --build
```

**Acceso:**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8081/api/impresion/simular

---

## Verificación (Criterio guía)
> **Diseño → Revisión → Impresión** — Verificar que ningún proceso avance a la siguiente etapa antes de tiempo

Orde esperado en logs (3 ciclos):
```
Documento 1 -> [DISEÑO] prepara documento.
Documento 1 -> [REVISIÓN] verifica documento.
Documento 1 -> [IMPRESIÓN] imprime documento.
---------------------------------------------------
Documento 2 -> [DISEÑO] prepara documento.
...
```

---

## Pseudocódigo (guía)
```
SEMÁFORO turno_diseno = 1
SEMÁFORO turno_revision = 0
SEMÁFORO turno_impresion = 0

PROCEDIMIENTO diseno()
    REPETIR 3 VECES
        wait(turno_diseno)
        escribir("Diseño prepara documento")
        crear_documento()
        signal(turno_revision)
    FIN REPETIR
FIN PROCEDIMIENTO

PROCEDIMIENTO revision()
    REPETIR 3 VECES
        wait(turno_revision)
        escribir("Revisión verifica documento")
        revisar_documento()
        signal(turno_impresion)
    FIN REPETIR
FIN PROCEDIMIENTO

PROCEDIMIENTO impresion()
    REPETIR 3 VECES
        wait(turno_impresion)
        escribir("Impresión imprime documento")
        imprimir_documento()
        signal(turno_diseno)
    FIN REPETIR
FIN PROCEDIMIENTO
```

---

## Pregunta de análisis
> ¿Qué ocurre si se elimina uno de los `signal()`?
- **Sin `signal(turno_revision)`**: Revisión nunca despierta → deadlock (Diseño produce 1 doc y se bloquea en 2da iteración)
- **Sin `signal(turno_impresion)`**: Impresión nunca despierta → Revisión se bloquea tras 1er doc
- **Sin `signal(turno_diseno)`**: Ciclo se rompe tras 1er documento → deadlock en 2da iteración