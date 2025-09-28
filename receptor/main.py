# receptor.py
import espnow
import network
import time
from machine import Pin
import machine
import json

# Pin del LED integrado en la ESP32-C3 Super Mini
LED_PIN = 8
led = Pin(LED_PIN, Pin.OUT)
taquilla1= Pin(0, Pin.OUT)
taquilla2= Pin(1, Pin.OUT)
taquilla3= Pin(2, Pin.OUT)
taquilla4= Pin(3, Pin.OUT)
taquillas=[taquilla1, taquilla2, taquilla3, taquilla4]
# Lógica del LED (activa con valor bajo)
def led_on():
    led.value(0)
def led_off():
    led.value(1)

# Parpadea el LED un número de veces
def blink(times, duration):
    for _ in range(times):
        led_on()
        time.sleep_ms(duration)
        led_off()
        time.sleep_ms(duration)
blink(5,100)

# Dirección MAC del transmisor (ESP32)
# Formato: 38:18:2b:84:a4:c0 -> b'\x38\x18\x2b\x84\xa4\xc0'
mac_centralita = b'\x38\x18\x2b\x84\xa4\xc0'

# Inicializa la interfaz de red para usar Wi-Fi en modo Estación
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

# Inicializa ESP-NOW
e = espnow.ESPNow()
e.active(True)
e.config(timeout_ms=-1)

# Añade el dispositivo transmisor
e.add_peer(mac_centralita)

print("Receptor ESP-NOW en marcha.")


def handshake():
    try:
        print('Esperando SYN...')
        
        host, msg = e.recv(timeout_ms=-1)
        if msg:
            if 'SYN' not in msg:
                blink(2,50)
                print('esperaba SYN, pero recibe:')
                print(msg)
                return True
#                 machine.reset()
            if 'SYN' in msg:
    #             blink(1,50)
                print('SYN recibido')
                success = e.send(mac_centralita, 'SYN-ACK')
            
                if success:
                    print('SYN-ACK enviado')
        #             blink(2,50)
                    print('##### CONEXIÓN ESTABLECIDA	#####')	
                    return True
#                 host, msg = e.recv()
#                 if msg:
#                     if 'ACK' in msg:
#                         print('##### CONEXIÓN ESTABLECIDA	#####')
#                         return True
    except:
        return False
        

while not handshake():
    blink(3,200)
blink(10,50)
print('esperando mensajes')
while True:
    
    host, msg = e.recv(timeout_ms=-1)
    if msg:
        blink(1,50)
        print(msg)
#         digito=int(str(msg)[-2])
#         if digito%2==0:
#             taquilla1.value(1)
#             taquilla2.value(0)
#             taquilla3.value(1)
#             taquilla4.value(0)
#         else:
#             taquilla1.value(0)
#             taquilla2.value(1)
#             taquilla3.value(0)
#             taquilla4.value(1)
#         blink(1,50)
        if 'SYN' in msg:
            machine.reset()
        if 'ocupar' or 'liberar' in msg:
            if '1' in msg:
                taquilla1.value(1)
                time.sleep(2)
                taquilla1.value(0)
            if '2' in msg:
                taquilla2.value(1)
                time.sleep(2)
                taquilla2.value(0)
            if '3' in msg:
                taquilla3.value(1)
                time.sleep(2)
                taquilla3.value(0)
            if '4' in msg:
                taquilla4.value(1)
                time.sleep(2)
                taquilla4.value(0)
#         if 'liberar' in msg:
#             if '1' in msg: taquilla1.value(0)
#             if '2' in msg: taquilla2.value(0)
#             if '3' in msg: taquilla3.value(0)
#             if '4' in msg: taquilla4.value(0)
        if 'no quedan taquillas' in msg:
            
            for i in range(1):
                for taquilla in taquillas:
                    taquilla.value(0)
                    time.sleep(0.1)
                for taquilla in taquillas:
                    taquilla.value(1)
                    time.sleep(0.1)
#     blink(100,200)

