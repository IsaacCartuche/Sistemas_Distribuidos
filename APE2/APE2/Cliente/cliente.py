import time

# Ruta hacia la carpeta compartida externa al proyecto
RUTA_ENTRADA = '../archivos_comunicacion/entrada_servidor.txt'
RUTA_SALIDA = '../archivos_comunicacion/salida_servidor.txt'

def iniciar_cliente():
    while True:
        mensaje = input("Ingrese un mensaje para el servidor (o 'salir' para terminar): ")
        if mensaje.lower() == 'salir':
            break

        # Escribir mensaje en la entrada
        with open(RUTA_ENTRADA, 'w') as f_entrada:
            f_entrada.write(mensaje)
        
        print("Mensaje enviado. Esperando respuesta (simulando latencia)...")
        # Simular latencia de red
        time.sleep(2) 
        
        # Leer respuesta desde la salida
        try:
            with open(RUTA_SALIDA, 'r') as f_salida:
                respuesta = f_salida.read().strip()
            print(f"Respuesta recibida del servidor: '{respuesta}'\n")
        except FileNotFoundError:
            print("Error: No se encontró el archivo de salida.\n")

if __name__ == "__main__":
    iniciar_cliente()