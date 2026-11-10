import requests


API_KEY = "api key"

# 2. Dirección exacta según la guía oficial
URL_COMPLETA = "url"

# 3. Prompt de prueba
prompt = 'Responde únicamente en JSON con el formato: {"estado": "OK"}'

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "qwen3-coder:30b",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "stream": False
}

try:
    print(f"Conectando a {URL_COMPLETA}...")
    response = requests.post(URL_COMPLETA, headers=headers, json=payload, timeout=15)
    
    # Valida automáticamente errores HTTP
    response.raise_for_status()

    resultado = response.json()
    texto = resultado["choices"][0]["message"]["content"]

    print("\n¡Conexión Exitosa!")
    print("Respuesta de la IA:", texto)

except Exception as err:
    print("\nError al conectar:", err)