# Importa las librerías necesarias para el proyecto.
# 'espnow' para la comunicación inalámbrica.
# 'network' para configurar la red Wi-Fi.
# 'time' para usar funciones de retardo.
# 'machine' para controlar los pines GPIO del ESP32.
# 'json' para manejar los datos de persistencia en formato JSON.
import espnow
import network
import time
from machine import Pin
import json

# Define el número del pin del LED integrado en el ESP32-C3 Super Mini.
LED_PIN = 8
# Crea un objeto 'Pin' para controlar el LED y lo configura como salida.
led = Pin(LED_PIN, Pin.OUT)

# Define y configura los pines para cada una de las cuatro taquillas.
taquilla1 = Pin(5, Pin.OUT)
taquilla2 = Pin(6, Pin.OUT)
taquilla3 = Pin(7, Pin.OUT)
taquilla4 = Pin(10, Pin.OUT)
# Crea una lista para organizar los objetos 'Pin' de las taquillas.
taquillas = [taquilla1, taquilla2, taquilla3, taquilla4]

# --- Funciones de control del LED ---

# Función para encender el LED. El LED es de tipo "ánodo común", por lo que
# se enciende con un valor de 0 (LOW).
def led_on():
    led.value(0)
    
# Función para apagar el LED. Se apaga con un valor de 1 (HIGH).
def led_off():
    led.value(1)

# Función para hacer parpadear el LED un número de veces.
# 'times' es el número de parpadeos y 'duration' es la duración de cada estado (encendido/apagado).
def blink(times, duration):
    for _ in range(times):
        led_on()
        time.sleep_ms(duration)
        led_off()
        time.sleep_ms(duration)
        
# Llama a la función 'blink' para parpadear el LED 5 veces con 100ms de duración.
# Esto sirve como una señal visual de que el programa ha comenzado.
blink(5, 100)

# Dirección MAC del ESP32 transmisor (centralita).
# Es la dirección a la que se enviarán las respuestas.
mac_centralita = b'\x38\x18\x2b\x84\xa4\xc0'


# --- Bloque de control de persistencia ---

# Intenta abrir el archivo llamado "persistencia" en modo lectura.
try:
    # Abre el archivo para leer el estado guardado.
    g = open("persistencia", "r")
    # Carga el contenido del archivo JSON en la variable 'data'.
    data = json.load(g)
    # Imprime un mensaje de éxito.
    print("json abierto")
    # Cierra el archivo.
    g.close()
    
    # Itera sobre los datos cargados para sincronizar el estado de los pines
    # de las taquillas con el estado guardado.
    for i in len(data):
        # Si el estado en el JSON es 'disponible', el pin se pone en 0 (liberado).
        if data[i] == 'disponible':
            taquillas[i].value(0)
        # Si no, el pin se pone en 1 (ocupado).
        else:
            taquillas[i].value(1)
            
# Si el archivo "persistencia" no existe, se ejecuta este bloque 'except'.
except:
    # Imprime un mensaje indicando que el archivo no se encontró.
    print("json no disponible. Creando json...")
    # Abre el archivo en modo escritura ('w') para crearlo.
    f = open("persistencia", "w")
    # Define el estado inicial de las taquillas como "disponible".
    taquillas = ['disponible', 'disponible' , 'disponible', 'disponible']
    # Escribe el estado inicial en el archivo en formato JSON.
    f.write(json.dumps(taquillas))
    # Cierra el archivo.
    f.close()
    # Imprime un mensaje de confirmación de que el archivo ha sido creado.
    print('json creado')

# --- Inicialización de ESP-NOW ---

# Inicializa la interfaz de red para Wi-Fi en modo Estación.
sta = network.WLAN(network.STA_IF)
# Activa la interfaz de Wi-Fi.
sta.active(True)
# Desconecta de cualquier red Wi-Fi a la que pudiera estar conectada.
sta.disconnect()

# Inicializa la librería ESP-NOW.
e = espnow.ESPNow()
# Activa el servicio ESP-NOW.
e.active(True)

# Añade la dirección MAC de la centralita (transmisor) como un par de confianza
# para poder enviar y recibir mensajes de ella.
e.add_peer(mac_centralita)

# Imprime un mensaje para indicar que el receptor está listo.
print("Receptor ESP-NOW en marcha. Esperando mensajes...")


# --- Bucle principal de funcionamiento ---

# Bucle infinito que se ejecuta continuamente.
while True:
    
    # Abre y lee el archivo de persistencia dentro del bucle.
    # Esto asegura que el estado más reciente se utilice.
    g = open("persistencia", "r")
    data = json.load(g)
    g.close()
    
    # Espera un mensaje de ESP-NOW. 'e.recv()' devuelve la dirección del emisor
    # ('host') y el mensaje ('msg').
    host, msg = e.recv()
    
    # Comprueba si se ha recibido un mensaje (si 'msg' no es None).
    if msg:
        # Si se recibe un mensaje, el LED parpadea una vez como señal de recepción.
        blink(1, 50)
        # Imprime la dirección del emisor y el contenido del mensaje.
        print("Mensaje recibido de:", host)
        # Decodifica el mensaje de bytes a una cadena de texto UTF-8.
        mensaje = msg.decode('utf-8')
        print("Mensaje:", mensaje)
        
        # Comprueba si la palabra 'liberar' está en el mensaje.
        if 'liberar' in mensaje:
            # Comprueba qué número de taquilla se debe liberar.
            if '1' in mensaje:
                taquilla1.value(0) # Pone el pin en 0 (liberado).
                
            if '2' in mensaje:
                taquilla2.value(0)
                
            if '3' in mensaje:
                taquilla3.value(0)
                
            if '4' in mensaje:
                taquilla4.value(0)
                
        # Comprueba si la palabra 'ocupar' está en el mensaje.
        if 'ocupar' in mensaje:
            # Comprueba qué número de taquilla se debe ocupar.
            if '1' in mensaje:
                taquilla1.value(1) # Pone el pin en 1 (ocupado).
                
            if '2' in mensaje:
                taquilla2.value(1)
                
            if '3' in mensaje:
                taquilla3.value(1)
                
            if '4' in mensaje:
                taquilla4.value(1)
                
            # Abre el archivo de persistencia en modo escritura.
            g = open("persistencia", "w")
            # Escribe el estado actual de las taquillas en el archivo.
            g.write(json.dumps(data))
            # Cierra el archivo para guardar los cambios.
            g.close()
