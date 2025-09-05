# emisor.py
# CÓDIGO PARA COMUNICARSE POR ESP NOW
# ESTE ARCHIVO CONTROLA EL EMISOR
# VA INSTALADO EN UN ESP32
import espnow
import network
import time
import json
from mfrc522 import MFRC522
import utime
import machine
from machine import Pin

# Dirección MAC del receptor (ESP32-C3)

mac_torre_1 = b'\x98\x88\xe0\xc9\x28\x1c'


# Inicializa la interfaz de red para usar Wi-Fi en modo Estación
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

# Inicializa ESP-NOW
e = espnow.ESPNow()
e.active(True)
# e.config(timeout_ms=-1)


# Añade los dispositivos receptores
e.add_peer(mac_torre_1)
print("Transmisor ESP-NOW en marcha. Enviando mensajes...")


# Pin del LED integrado en la ESP32
LED_PIN = 2
led = Pin(LED_PIN, Pin.OUT)

# Lógica del LED (activa con valor alto)
def led_on():
    led.value(1)
def led_off():
    led.value(0)

# Parpadea el LED un número de veces
def blink(times, duration):
    for _ in range(times):
        led_on()
        time.sleep_ms(duration)
        led_off()
        time.sleep_ms(duration)

blink(5,100)

def handshake():
    try:
        print("Iniciando handshake con el receptor...")
        e.config(timeout_ms=3000)
        success = e.send(mac_torre_1, 'SYN')    

        print('SYN enviado. Esperando respuesta')
#         blink(1,200)
        host, msg = e.recv()
        if msg:
#             blink(2,200)        
            if 'SYN' in msg and 'ACK' in msg:
                print('SYN-ACK recibido')
                success = e.send(mac_torre_1, 'ACK')
#                 blink(3,200)

                print('''ACK enviado.
                #####	CONEXIÓN ESTABLECIDA	#####''')
                return True    
        else:
            print("Fallo en el handshake. Reintentando...")
            blink(3,100)
            time.sleep(1)
            return False
    except:
        time.sleep(1)
        return False

while not handshake():
    time.sleep(1)
blink(10,50)
while True:
    blink(100,200)
