# APE 4 — Mecanismos de Comunicación IPC y Red

## Descripción
Implementación de un sistema de asignación de pedidos (tipo delivery) que integra:
- Comunicación entre procesos (IPC) usando colas y memoria compartida
- Comunicación en red mediante sockets TCP
- Agente de decisión basado en IA (Ollama) para asignación de tareas según carga y distancia

## Arquitectura propuesta

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVIDOR CENTRAL                             │
│  ┌──────────────┐    IPC (Queue + Shared Memory)    ┌───────────┐  │
│  │  Generador   │ ─────────────────────────────────► │ Procesador│  │
│  │  (productor) │   flota/{vehiculo}/pedidos        │ (consumer)│  │
│  └──────────────┘                                    └─────┬─────┘  │
│                                                             │      │
│                              TCP Socket                     ▼      │
│  ┌──────────────┐                                    ┌───────────┐  │
│  │   Gateway    │ ◄───────────────────────────────── │  Ollama   │  │
│  │  (bridge.py) │   Decide qué worker recibe pedido  │  (local)  │  │
│  └──────┬───────┘                                    └───────────┘  │
│         │                                                    ▲      │
│         │ TCP                                                │      │
│         ▼                                                    │      │
│  ┌──────────────┐                                    ┌───────────┐  │
│  │   Worker 1   │                                    │           │  │
│  │ (servidor.py)│                                    │           │  │
│  └──────────────┘                                    │           │  │
│  ┌──────────────┐                                    │  Workers  │  │
│  │   Worker 2   │                                    │  remotos  │  │
│  │ (servidor.py)│                                    │           │  │
│  └──────────────┘                                    └───────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Componentes

| Componente | Archivo | Función |
|------------|---------|---------|
| Generador de pedidos | `cliente_system/ipc_system/controls/productor.py` | Crea pedidos y los coloca en cola IPC |
| Procesador | `cliente_system/ipc_system/controls/procesador.py` | Extrae pedidos, calcula alerta, guarda en memoria compartida |
| Cliente IPC | `cliente_system/cliente.py` | Lee memoria compartida y envía por TCP al Gateway |
| Gateway + IA | `gateway-system/gateway.py` | Recibe pedidos, consulta Ollama, decide worker destino |
| Workers | `servidores-system/server.py` | Reciben pedidos por TCP y procesan |
| Orquestador | `cliente_system/ipc_system/main.py` / `cliente_system/app.py` | Inicia IPC + hilos cliente |

## Flujo de datos

1. **Generador** → Cola IPC (`multiprocessing.Queue`)
2. **Procesador** ← Cola IPC → Memoria compartida (`Manager.dict`)
3. **Cliente** ← Memoria compartida → Socket TCP → **Gateway**
4. **Gateway** → HTTP POST a **Ollama** (puerto 11434) → Decide worker
5. **Gateway** → Socket TCP → **Worker** seleccionado

## Tecnologías

- Python 3.x
- `multiprocessing` (Queue, Manager.dict, Process)
- `socket` (TCP)
- `requests` (Ollama API)
- Ollama (modelo local, ej. `codegeex4`)

## Puertos

| Servicio | Puerto | Protocolo |
|----------|--------|-----------|
| Gateway (escucha clientes) | 6000 | TCP |
| Worker 1 | 7001 | TCP |
| Worker 2 | 7002 | TCP |
| Ollama API | 11434 | HTTP |

## Preguntas de control (guía)

1. Diferencia entre comunicación IPC (cola procesos) y sockets TCP
2. Por qué el agente IA y el generador pueden ejecutarse en computadoras distintas sin compartir memoria
3. Qué información debe viajar en el mensaje para que el agente decida correctamente; qué pasa si falta la carga del nodo
4. Qué ocurre si un worker se desconecta mientras hay pedidos en la cola
5. En qué casos un agente de IA aporta valor frente a reglas fijas y en cuáles no