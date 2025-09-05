# Archivo de control para el transmisor ESP-NOW
# Este script se carga en una placa ESP32 y se encarga de:
# 1. Leer etiquetas RFID.
# 2. Gestionar el estado de "taquillas" (ocupadas/libres) en un archivo local.
# 3. Enviar mensajes a una ESP32-C3 (el receptor) a través de ESP-NOW para controlar las taquillas.

# -- IMPORTACIONES DE LIBRERÍAS --
# ESP-NOW, red y tiempo son necesarios para la comunicación inalámbrica.
import espnow
import network
import time
# JSON se usa para leer y escribir en el archivo de persistencia.
import json

# MFRC522 y machine son para interactuar con el lector RFID y el hardware.
from mfrc522 import MFRC522
import utime
import machine
from machine import Pin

# -- CONFIGURACIÓN INICIAL DEL HARDWARE --
# Se inicializa el lector RFID MFRC522 con los pines SPI y RST.
# spi_id=5, sck=14, miso=12, mosi=13, cs=26, rst=27 son la configuración para el hardware específico.
lector = MFRC522(spi_id=5,sck=14,miso=12,mosi=13,cs=26,rst=27)
print("lector OK")

# Se inicializa el LED integrado de la placa ESP32
LED_PIN = 2
led = Pin(LED_PIN, Pin.OUT)
# Se definen las funciones para controlar el LED
def led_on():
    led.value(1)
def led_off():
    led.value(0)
def blink(times, duration):
    """Hace parpadear el LED un número de veces con una duración específica."""
    for _ in range(times):
        led_on()
        time.sleep_ms(duration)
        led_off()
        time.sleep_ms(duration)


# Parpadea el LED al inicio para indicar que el programa ha arrancado.
blink(5,100)

# -- CONFIGURACIÓN DE ESP-NOW --
# Se definen las direcciones MAC de los dispositivos receptores (las "torres").
# Nota: Todas las MAC de las torres son iguales en este código, lo cual es inusual si son placas diferentes.
receiver_mac = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_1 = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_2 = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_3 = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_4 = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_5 = b'\x98\x88\xe0\xc9\x28\x1c'
torres=[mac_torre_1,mac_torre_2,mac_torre_3,mac_torre_4, mac_torre_5]

# Se configura la interfaz Wi-Fi de la ESP32 en modo estación.
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

# Se inicializa el objeto ESP-NOW.
e = espnow.ESPNow()
e.active(True)
# Configura un tiempo de espera infinito para la función de envío.
e.config(timeout_ms=-1)

# Se añade el "peer" (dispositivo receptor) al que se enviarán los mensajes.
e.add_peer(receiver_mac)
# # ALTERNATIVA Se usa un bloque try-except para manejar el caso en que el peer ya esté añadido.
# try:
#     e.add_peer(receiver_mac)
#     # Se añaden otros peers para la compatibilidad, aunque ya esté añadido.
#     e.add_peer(mac_torre_1)
# except ValueError:
#     print("El peer ya existe. No se añadió de nuevo.")
# except:
#     pass # No hace nada si hay otro error.
print("Transmisor ESP-NOW en marcha. Enviando mensajes...")

# -- GESTIÓN DE PERSISTENCIA (ARCHIVO JSON) --
# Este bloque de código gestiona un archivo llamado "persistencia" para guardar el estado de las taquillas.
# Si el archivo existe, lo lee; si no, lo crea con un estado inicial.
try:
    g=open("persistencia", "r")
    data=json.load(g)
    print("json abierto")
    g.close()
except:
    print("json no disponible. Creando archivo...")
    f=open("persistencia", "w")
    taquillas=[
        {'nombre':'1', 'torre': 1, 'GPIO' : 5,'tarjeta': '',"fecha_inicio":0},
        {'nombre':'2','torre': 1, 'GPIO' : 6,'tarjeta': "","fecha_inicio":0},
        {'nombre':'3','torre': 1, 'GPIO' : 7,'tarjeta': "","fecha_inicio":0},
        {'nombre':'4','torre': 1, 'GPIO' : 9,'tarjeta': "","fecha_inicio":0}
    ]
    f.write(json.dumps(taquillas))
    f.close()

# -- BUCLE PRINCIPAL --
# Bucle infinito para la operación continua del programa.
while True:
    # Lee los datos actualizados del archivo de persistencia en cada iteración del bucle.
    g=open("persistencia", "r")
    data=json.load(g)
    g.close()

    # Inicializa el lector RFID para cada intento de lectura.
    lector.init()
    # Solicita una etiqueta RFID y espera a que una esté presente.
    (stat, tag_type) = lector.request(lector.REQIDL)
    
    # -- LÓGICA SI SE DETECTA UNA TARJETA --
    if stat == lector.OK:
        # Si se detecta una etiqueta, la selecciona para obtener su UID.
        (stat, uid) = lector.SelectTagSN()
        
        # Convierte el UID (byte array) a un número entero.
        identificador = int.from_bytes(bytes(uid),"little",False)
        tarjeta=identificador
        asignada=False
        
        # Bucle para buscar la tarjeta en el archivo de persistencia.
        for taquilla in data:
            if tarjeta == taquilla['tarjeta']:
                # Si la tarjeta ya está asignada, se prepara el mensaje para "liberar" la taquilla.
                message='liberar'+taquilla['nombre']
                taquilla_ocupada=taquilla
                asignada=True
                # Se determina la MAC del receptor basándose en el número de torre.
                # Nota: En el JSON inicial, todas las torres son la 1.
                if taquilla['torre']==1:
                    receiver_mac=mac_torre_1
                if taquilla['torre']==2:
                    receiver_mac=mac_torre_2
                if taquilla['torre']==3:
                    receiver_mac=mac_torre_3
                if taquilla['torre']==4:
                    receiver_mac=mac_torre_4
                if taquilla['torre']==5:
                    receiver_mac=mac_torre_5
                
                # Se actualiza el estado de la taquilla a libre en el archivo de persistencia.
                taquilla['tarjeta']=''
                g=open("persistencia", "w")
                g.write(json.dumps(data))
                g.close()
                print('taquilla ' + taquilla['nombre']+ ' liberada')
                break # Sale del bucle una vez que la tarjeta ha sido procesada.
        
        # Si la tarjeta no estaba asignada, se busca una taquilla libre.
        if not asignada:
            todo_ocupado=True
            for taquilla in data:
                if taquilla['tarjeta']=='':
                    # Si se encuentra una taquilla libre, se le asigna la tarjeta.
                    taquilla['tarjeta']=tarjeta
                    # Se prepara el mensaje para "ocupar" la taquilla.
                    message='ocupar'+taquilla['nombre']
                    # Se actualiza el estado de la taquilla en el archivo.
                    g=open("persistencia", "w")
                    g.write(json.dumps(data))
                    g.close()
                    print('ocupa la taquilla ' + taquilla['nombre'])
                    todo_ocupado=False
                    # Se determina la MAC del receptor según el número de torre.
                    if taquilla['torre']==1:
                        receiver_mac=mac_torre_1
                    if taquilla['torre']==2:
                        receiver_mac=mac_torre_2
                    if taquilla['torre']==3:
                        receiver_mac=mac_torre_3
                    if taquilla['torre']==4:
                        receiver_mac=mac_torre_4
                    if taquilla['torre']==5:
                        receiver_mac=mac_torre_5
                    break # Sale del bucle.
            if todo_ocupado:
                print('no quedan taquillas disponibles')
        
        # -- ENVÍO DEL MENSAJE ESP-NOW --
        # Envía el mensaje preparado a la MAC del receptor.
        success = e.send(receiver_mac, message)
        print('mensaje enviado: ' + message)
        
        if success:
            print("Mensaje enviado con éxito.")
            blink(1, 50) # Parpadeo corto para indicar éxito.
        else:
            print("Error al enviar el mensaje.")
            blink(3, 100) # Parpadeo más largo para indicar fallo.
        time.sleep(3) # IMPRESCINDIBLE Espera 3 segundos antes de la siguiente lectura.

    # -- LÓGICA SI NO SE DETECTA NINGUNA TARJETA --
    else:
        print("esperando")
        message = "esperando"
        # Bucle para reintentar el envío del mensaje de "espera" con un retraso incremental.
        for i in range(5):
            try:
                success = e.send(receiver_mac, message)
                fallo=False
                break # Sale del bucle si el envío es exitoso.
            except:
                blink(3,200)
                print(f'intento fallido nº {i}')
                time.sleep(0.1+(i*0.1))
                fallo=True
        if fallo:
            machine.reset()
        
        if success:
            print("Mensaje enviado con éxito.")
            blink(1, 50) # Parpadeo corto para indicar éxito.
        else:
            print("Error al enviar el mensaje.")
            blink(3, 100) # Parpadeo más largo para indicar fallo.
        time.sleep(1) # Espera 1 segundo.
        blink(1,100)
    
    time.sleep(2)
