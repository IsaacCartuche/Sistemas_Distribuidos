# APE 2 — Arquitectura Cliente-Servidor con Comunicación por Archivos

## Objetivo
Comprender la arquitectura de sistemas distribuidos mediante el desarrollo independiente de sus componentes (cliente y servidor) comunicados a través de un canal compartido (archivos de texto).

---

## Arquitectura

```
┌─────────────┐     /comunicacion/      ┌─────────────┐
│   Cliente   │ ──────────────────────► │  Servidor   │
│  (cliente.py)│  entrada_servidor.txt  │ (servidor.py)│
└─────────────┘                         └─────────────┘
       ▲                                        │
       │         salida_servidor.txt            │
       └────────────────────────────────────────┘
                (respuesta procesada)
```

- **Comunicación indirecta**: Cliente y servidor no se conocen directamente, solo comparten archivos
- **Desacoplamiento**: Cada componente se desarrolla y ejecuta independientemente
- **Procesamiento**: El servidor convierte el mensaje a mayúsculas

---

## Estructura del proyecto

```
APE2/APE2/
├── Cliente/
│   └── cliente.py          # Cliente interactivo
├── Servidor/
│   └── servidor.py         # Servidor daemon (polling 1s)
├── Dockerfile.cliente      # Imagen del cliente
├── Dockerfile.servidor     # Imagen del servidor
├── docker-compose.yml      # Orquestación (shared volume)
├── documentacion.odt       # Documentación original
├── entrada_servidor.txt    # Archivo de entrada (legacy)
├── salida_servidor.txt     # Archivo de salida (legacy)
└── README.md               # Este archivo
```

---

## Requisitos
- Docker + Docker Compose
- (Opcional) Python 3.11+ para ejecución local sin Docker

---

## Ejecución con Docker (recomendado)

```bash
cd /home/isaac/Documents/Sistemas_Distribuidos/APE2/APE2

# Construir y levantar ambos contenedores
docker compose up --build -d servidor

# Ver logs del servidor
docker compose logs -f servidor

# En otra terminal: ejecutar cliente interactivo
docker compose run --rm cliente
```

**Dentro del cliente:**
```
Ingrese un mensaje para el servidor (o 'salir' para terminar): hola mundo
Mensaje enviado. Esperando respuesta (simulando latencia)...
Respuesta recibida del servidor: 'HOLA MUNDO'

Ingrese un mensaje para el servidor (o 'salir' para terminar): prueba docker
Mensaje enviado. Esperando respuesta (simulando latencia)...
Respuesta recibida del servidor: 'PRUEBA DOCKER'

Ingrese un mensaje para el servidor (o 'salir' para terminar): salir
```

**Verificar archivos de comunicación:**
```bash
# Desde el host (volume montado en /var/lib/docker/volumes/ape2_ape2-comunicacion/_data)
docker compose exec servidor cat /comunicacion/entrada_servidor.txt
docker compose exec servidor cat /comunicacion/salida_servidor.txt
```

---

## Ejecución local (sin Docker)

```bash
cd /home/isaac/Documents/Sistemas_Distribuidos/APE2/APE2

# Terminal 1: Servidor
mkdir -p archivos_comunicacion
python Servidor/servidor.py

# Terminal 2: Cliente
python Cliente/cliente.py
```

---

## Resultados esperados (según guía)

| Entregable | Estado |
|------------|--------|
| Código fuente `servidor.py` y `cliente.py` en Git | ✅ |
| Capturas: entrada_servidor.txt llenado por cliente | 📸 Pendiente |
| Capturas: salida_servidor.txt con resultado procesado | 📸 Pendiente |
| Capturas: ≥3 mensajes procesados correctamente | 📸 Pendiente |
| Respuestas a preguntas de control en reporte | 📝 Pendiente |
| **Dockerizado y funcional en local** | ✅ |

---

## Preguntas de control (para el reporte)

1. ¿Qué significa que cliente y servidor estén desacoplados?
2. ¿Qué ventajas tiene desarrollar componentes por separado?
3. ¿Qué problemas pueden surgir al integrar sistemas independientes?
4. ¿Qué sucede si el servidor no está ejecutándose?
5. ¿Cómo se simula la comunicación en esta práctica?
6. ¿Qué limitaciones tiene este modelo frente a uno real?
7. ¿Cómo se podría mejorar la sincronización?
8. ¿Qué pasaría si múltiples clientes usan el sistema?

---

## Notas técnicas

- **Polling**: El servidor revisa el archivo cada 1 segundo (`time.sleep(1)`)
- **Deduplicación**: Usa `ultimo_mensaje` para no reprocesar el mismo contenido
- **Latencia simulada**: Cliente espera 2s antes de leer respuesta
- **Volumen compartido**: `comunicacion` (Docker named volume) permite intercambio entre contenedores
- **Cliente interactivo**: Requiere `stdin_open: true` y `tty: true` en docker-compose