import requests
import json

# URL y clave según la configuración del servidor
URL_COMPLETA = "http://10.20.202.199:3000/api/chat/completions"
API_KEY = "sk-7f042ec1532e4cddb129cb42744871a1"
MODELO = "qwen3-coder:30b"

def decidir_worker(pedido, estado_workers):
    prompt = f"""
    Eres un asignador inteligente de un sistema de delivery distribuido.
    Asigna el siguiente pedido al worker más adecuado (7001 o 7002):

    DATOS DEL PEDIDO:
    - ID: {pedido['id_pedido']}
    - Distancia del cliente: {pedido['distancia_km']} km
    - Prioridad: {pedido['prioridad']}

    ESTADO ACTUAL DE LOS WORKERS:
    - Worker 7001: Distancia = {estado_workers['7001']['distancia']} km, Carga actual = {estado_workers['7001']['carga']} pedidos
    - Worker 7002: Distancia = {estado_workers['7002']['distancia']} km, Carga actual = {estado_workers['7002']['carga']} pedidos

    Criterio: Balancear la carga sin descuidar pedidos de alta prioridad o distancias lejanas.
    Responde ÚNICAMENTE un JSON válido con esta estructura exacta:
    {{"worker_seleccionado": "7001" o "7002", "razon": "explicación breve"}}
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODELO,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    try:
        response = requests.post(URL_COMPLETA, headers=headers, json=payload, timeout=12)
        response.raise_for_status()
        
        resultado = response.json()
        texto_respuesta = resultado["choices"][0]["message"]["content"]
        
        return json.loads(texto_respuesta)

    except Exception as e:
        print(f"[Agente IA Error] {e}. Aplicando regla fija de respaldo.")
        if estado_workers['7001']['carga'] <= estado_workers['7002']['carga']:
            return {"worker_seleccionado": "7001", "razon": "Respaldo: Menor carga"}
        return {"worker_seleccionado": "7002", "razon": "Respaldo: Menor carga"}