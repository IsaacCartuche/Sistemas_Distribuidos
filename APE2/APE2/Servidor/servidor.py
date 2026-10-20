import time
import os

# Ruta hacia la carpeta compartida externa al proyecto
RUTA_ENTRADA = '../archivos_comunicacion/entrada_servidor.txt'
RUTA_SALIDA = '../archivos_comunicacion/salida_servidor.txt'

def iniciar_servidor():
    print("Servidor activo. Esperando nuevos mensajes...")
    ultimo_mensaje = ""

    # Asegurar que los archivos existan
    os.makedirs('../archivos_comunicacion', exist_ok=True)
    open(RUTA_ENTRADA, 'a').close()
    open(RUTA_SALIDA, 'a').close()

    while True:
        try:
            with open(RUTA_ENTRADA, 'r') as f_entrada:
                mensaje = f_entrada.read().strip()

            # Detectar contenido nuevo y manejar archivos vacíos
            if mensaje and mensaje != ultimo_mensaje:
                print(f"[+] Nuevo mensaje detectado: '{mensaje}'")
                
                # Procesamiento del mensaje (convertir a mayúsculas)
                mensaje_procesado = mensaje.upper()
                
                # Escribir resultado en el archivo de salida
                with open(RUTA_SALIDA, 'w') as f_salida:
                    f_salida.write(mensaje_procesado)
                
                print(f"[-] Resultado guardado: '{mensaje_procesado}'\n")
                ultimo_mensaje = mensaje

        except FileNotFoundError:
            pass # Evita errores si el archivo es eliminado accidentalmente
        
        # Revisión periódica
        time.sleep(1) 

if __name__ == "__main__":
    iniciar_servidor()