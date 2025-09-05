import espnow
import network
import time
from machine import Pin
import json

# Pin del LED integrado en la ESP32-C3 Super Mini
LED_PIN = 8
led = Pin(LED_PIN, Pin.OUT)
taquilla1= Pin(5, Pin.OUT)
taquilla2= Pin(6, Pin.OUT)
taquilla3= Pin(7, Pin.OUT)
taquilla4= Pin(8, Pin.OUT)
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
# transmitter_mac = b'\x38\x18\x2b\x84\xa4\xc0'


##### COMPRUEBA SI EXISTE EL ARCHIVO DE PERSISTENCIA	#####
try:
    g=open("persistencia", "r")
    data=json.load(g)
#     print(data)
    print("json abierto")
    g.close()
    for i in len(data):
        if data[i]=='disponible':
            taquillas[i].value(0)
        else:
            taquillas[i].value(1)
            
        
#####	SI EL ARCHIVO NO EXISTE, LO CREA Y LO PUEBLA	#####
except:
    print("json no disponible. Creando json...")
    f=open("persistencia", "w")
    taquillas=['disponible', 'disponible' , 'disponible', 'disponible']  
    f.write(json.dumps(taquillas))
    f.close()
    print('json creado')

# Inicializa la interfaz de red para usar Wi-Fi en modo Estación
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

# Inicializa ESP-NOW
e = espnow.ESPNow()
e.active(True)

# Añade el dispositivo transmisor
e.add_peer(mac_centralita)

print("Receptor ESP-NOW en marcha. Esperando mensajes...")


#####	LOOP DE FUNCIONAMIENTO	#####
while True:
    
    g=open("persistencia", "r")
    data=json.load(g)
    g.close()
    
    host, msg = e.recv()
    if msg:
        print("Mensaje recibido de:", host)
        mensaje=msg.decode('utf-8')
        print("Mensaje:", msg.decode('utf-8'))
#         print('respondiendo...')
#         mensaje='recibido OK'
#         success=e.send(mac_centralita, mensaje)
#         if success:
#             break
#         else:
#             print('fallo al contestar a la centralita')
        if 'liberar' in mensaje:
            if '1' in mensaje:
                taquilla1.value(0)
                
            if '2' in mensaje:
                taquilla2.value(0)
                
            if '3' in mensaje:
                taquilla3.value(0)
                
            if '4' in mensaje:
                taquilla4.value(0)
               
            
        if 'ocupar' in mensaje:
            if '1' in mensaje:
                taquilla1.value(1)
                
            if '2' in mensaje:
                taquilla2.value(1)
              
            if '3' in mensaje:
                taquilla3.value(1)
                
            if '4' in mensaje:
                taquilla4.value(1)
                
            g=open("persistencia", "w")
            g.write(json.dumps(data))
            g.close()
            

        blink(3, 100)
        



