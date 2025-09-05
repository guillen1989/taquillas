# CÓDIGO PARA COMUNICARSE POR ESP NOW
# ESTE ARCHIVO CONTROLA EL EMISOR
# VA INSTALADO EN UN ESP32
import espnow
import network
import time
import json

#### LEER TAG ####

from mfrc522 import MFRC522


lector = MFRC522(spi_id=5,sck=14,miso=12,mosi=13,cs=26,rst=27)
print("lector OK")
import utime
import machine
from machine import Pin
# Dirección MAC del receptor (ESP32-C3)
# Formato: 98:88:e0:c9:28:1c -> b'\x98\x88\xe0\xc9\x28\x1c'
receiver_mac = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_1 = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_2 = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_3 = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_4 = b'\x98\x88\xe0\xc9\x28\x1c'
mac_torre_5 = b'\x98\x88\xe0\xc9\x28\x1c'
torres=[mac_torre_1,mac_torre_2,mac_torre_3,mac_torre_4, mac_torre_5]
# Inicializa la interfaz de red para usar Wi-Fi en modo Estación
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()

# Inicializa ESP-NOW
e = espnow.ESPNow()
e.active(True)
e.config(timeout_ms=-1)

# Añade el dispositivo receptor
e.add_peer(receiver_mac)
try:
    e.add_peer(mac_torre_1)
except:
    pass
print("Transmisor ESP-NOW en marcha. Enviando mensajes...")
#lector = MFRC522(spi_id=0,sck=2,miso=4,mosi=3,cs=1,rst=0)
LED = machine.Pin(2,machine.Pin.OUT)
print("Lector activo...\n")


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

def parpadeo(elemento, repeticiones):
    for i in range(repeticiones):
    
        elemento.value(1)
        utime.sleep_ms(100) 
        elemento.value(0)
        utime.sleep_ms(100)
blink(5,100)

##### COMPRUEBA SI EXISTE EL ARCHIVO DE PERSISTENCIA	#####
try:
    g=open("persistencia", "r")
    data=json.load(g)
#     print(data)
    print("json abierto")
    g.close()
#####	SI EL ARCHIVO NO EXISTE, LO CREA Y LO PUEBLA	#####
except:
    print("json no disponible")
    f=open("persistencia", "w")
    taquillas=[
        {'nombre':'1', 'torre': 1,
        'GPIO' : 5,'tarjeta': '',"fecha_inicio":0},
        {'nombre':'2','torre': 1,
        'GPIO' : 6,'tarjeta': "","fecha_inicio":0},
        {'nombre':'3','torre': 1,
        'GPIO' : 7,'tarjeta': "","fecha_inicio":0},
        {'nombre':'4','torre': 1,
        'GPIO' : 9,'tarjeta': "","fecha_inicio":0}    
                                                   ]
    
                
    f.write(json.dumps(taquillas))
    f.close()


#####	LOOP DE FUNCIONAMIENTO	#####
while True:
    g=open("persistencia", "r")
    data=json.load(g)
    g.close()
    taquilla1=data[0]
    taquilla2=data[1]
    taquilla3=data[2]
    taquilla4=data[3]
#     print('tarjeta de la taquilla1: ' + taquilla1['tarjeta'])

    lector.init()
    (stat, tag_type) = lector.request(lector.REQIDL)
    if stat == lector.OK:
        (stat, uid) = lector.SelectTagSN()
        
        identificador = int.from_bytes(bytes(uid),"little",False)
#         print("UID: "+str(identificador))
        message = str(identificador)
        tarjeta=identificador
        asignada=False
        for taquilla in data:
            if tarjeta == taquilla['tarjeta']:
                
                
                message='liberar'+taquilla['nombre']
                taquilla_ocupada=taquilla
                asignada=True
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
                # GRABAR EN EL JSON QUE SE LIBERA LA TAQUILLA
                taquilla['tarjeta']=''
                g=open("persistencia", "w")
                g.write(json.dumps(data))
                g.close()
                print('taquilla ' + taquilla['nombre']+ ' liberada')
                
                break
            
            
        if not asignada:
            
        
            todo_ocupado=True
            for taquilla in data:
                if taquilla['tarjeta']=='':
                    taquilla['tarjeta']=tarjeta
                    #ENVIAR EL MENSAJE DE ABRIR LA FILA X DE LA TORRE CON MAC Y
                    message='ocupar'+taquilla['nombre']
                    # GRABAR EN EL JSON EL NÚMERO DE TARJETA
                    g=open("persistencia", "w")
                    g.write(json.dumps(data))
                    g.close()
                    print('ocupa la taquilla ' + taquilla['nombre'])
                    todo_ocupado=False
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
                    break
            if todo_ocupado:
                print('no quedan taquillas disponibles')
        
        success = e.send(receiver_mac, message)
        
        
        if success:
            print("RECIBIDO enviado con éxito.")
    # Parpadea el LED para indicar el envío
            blink(1, 50)
        else:
            print("Error al enviar el RECIBIDO.")
            # Parpadea el LED de forma diferente para indicar un fallo
            blink(3, 100)
        time.sleep(3)
    else:
        print("esperando")
        
        message = "esperando"
        for i in range(30):
            try:
                success = e.send(receiver_mac, message)
                break
            except:
                print(f'intento fallido nº {i}')
                time.sleep(0.1+(i*0.1))
        
        
        if success:
            print("Mensaje enviado con éxito.")
    # Parpadea el LED para indicar el envío
            blink(1, 50)
        else:
            print("Error al enviar el mensaje.")
#             print(success)
            # Parpadea el LED de forma diferente para indicar un fallo
            blink(3, 100)
        time.sleep(1)
        #parpadeo(LED,1)
        blink(1,100)
        

             
time.sleep(3) 





