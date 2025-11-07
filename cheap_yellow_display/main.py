import network
import gc
import json
import espnow
import sys
from machine import Pin, SPI, UART
import machine
import time
from xpt2046 import Touch
# Save this file as ili9341.py https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py
from ili9341 import Display, color565
# Save this file as xglcd_font.py https://github.com/rdagger/micropython-ili9341/blob/master/xglcd_font.py
from xglcd_font import XglcdFont

gc.collect() # Recolección inicial

# 🎨 VARIABLES GLOBALES DE PANTALLA (Creadas una única vez)
white_color = color565(255, 255, 255)  # white color
black_color = color565(0, 0, 0)        # black color
spi = SPI(1, baudrate=10000000, mosi=Pin(13), miso=Pin(12), sck=Pin(14))
cs = Pin(33, Pin.OUT)
irq = Pin(0, Pin.IN, Pin.PULL_UP)
display = Display(spi, dc=Pin(2), cs=Pin(15), rst=Pin(15),
          width=320, height=480, rotation=0)
touch = Touch(spi, cs=cs, int_pin=irq, int_handler=None,
             width=320, height=480)
backlight = Pin(27, Pin.OUT)
backlight.on()
# Objeto de fuente creado UNA SOLA VEZ
font = XglcdFont('fonts/Dejavu24x43.c', 24, 43)

# ⌨️ ESTRUCTURA DEL TECLADO (MOVIDA A GLOBAL para que se cree UNA SOLA VEZ)
TECLADO_COORDS = [
    {'tipo':'h','x':0, 'y':100, 'w':319},
    {'tipo':'h','x':0, 'y':195, 'w':319},
    {'tipo':'h','x':0, 'y':290, 'w':319},
    {'tipo':'h','x':0, 'y':385, 'w':319},
    {'tipo':'v','x':106, 'y':100, 'w':379},
    {'tipo':'v','x':214, 'y':100, 'w':379},
    {'tipo':'1', 'y':137, 'x':33, 'w':0},
    {'tipo':'2', 'y':137, 'x':140, 'w':0},
    {'tipo':'3', 'y':137, 'x':247, 'w':0},
    {'tipo':'4', 'y':232, 'x':33, 'w':0},
    {'tipo':'5', 'y':232, 'x':140, 'w':0},
    {'tipo':'6', 'y':232, 'x':247, 'w':0},
    {'tipo':'7', 'y':327, 'x':33, 'w':0},
    {'tipo':'8', 'y':327, 'x':140, 'w':0},
    {'tipo':'9', 'y':327, 'x':247, 'w':0},
    {'tipo':'DEL', 'y':422, 'x':10, 'w':0},
    {'tipo':'0', 'y':422, 'x':140, 'w':0},
    {'tipo':'ENT', 'y':422, 'x':225, 'w':0}
]

# VARIABLES ESP NOW
receiver_mac = b'\x98\x88\xe0\xc9\x28\x1c'
# CONFIGURACIÓN Y ARRANQUE ESP NOW
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()
e = espnow.ESPNow()
e.active(True)
e.config(timeout_ms=-1)
e.add_peer(receiver_mac)
if e:
    print("ESP NOW en marcha")


rojo =4
verde =17
azul =16

# VARIABLES UART
UART_ID = 1
TX_PIN = 22
RX_PIN = 21

# Configuración del UART
try:
    uart = UART(UART_ID, baudrate=115200, tx=Pin(TX_PIN), rx=Pin(RX_PIN))
    print("UART Receptor iniciado. Esperando datos...")
except:
    print("Error activando UART")

# Se definen las funciones para controlar el LED

def blink(led,times, duration):
    """Hace parpadear el LED un número de veces con una duración específica."""
    led = Pin(led, Pin.OUT)
    for _ in range(times):
        led.value(0)
        time.sleep_ms(duration)
        led.value(1)
        time.sleep_ms(duration)

blink(verde,5,100)

# FUNCIÓN formar_teclado OPTIMIZADA
def formar_teclado(borrar=False):
    # Se usan las variables globales (white_color, black_color, font, TECLADO_COORDS)
    if not borrar:
        char_color=white_color
    if borrar:
        char_color=black_color
    for line in TECLADO_COORDS:
        if line['tipo']=='h':
            display.draw_hline( line['x'],line['y'],line['w'], char_color)
        if line['tipo']=='v':
            display.draw_vline( line['x'],line['y'],line['w'], char_color)
        if line['tipo']!='h'and line['tipo']!='v':
            display.draw_text(line['x'],line['y'] , line['tipo'], font, char_color, black_color)

def detectar_valores(coordenadas):
    # Esta lista de coordenadas es pequeña y local, no impacta significativamente en la memoria.
    teclas_coords=[
    {'valor':'1', 'x_inf':254, 'x_sup':736, 'y_inf':510, 'y_sup':1024},
    {'valor':'2', 'x_inf':736, 'x_sup':1536, 'y_inf':510, 'y_sup':1024},
    {'valor':'3', 'x_inf':1536, 'x_sup':2000, 'y_inf':510, 'y_sup':1024},

    {'valor':'4', 'x_inf':254, 'x_sup':736, 'y_inf':1024, 'y_sup':1536},
    {'valor':'5', 'x_inf':736, 'x_sup':1536, 'y_inf':1024, 'y_sup':1536},
    {'valor':'6', 'x_inf':1536, 'x_sup':2000, 'y_inf':1024, 'y_sup':1536},

    {'valor':'7', 'x_inf':254, 'x_sup':736, 'y_inf':1536, 'y_sup':1616},
    {'valor':'8', 'x_inf':736, 'x_sup':1536, 'y_inf':1536, 'y_sup':1616},
    {'valor':'9', 'x_inf':1536, 'x_sup':2000, 'y_inf':1536, 'y_sup':1616},

    {'valor':'DEL', 'x_inf':254, 'x_sup':736, 'y_inf':1616, 'y_sup':2000},
    {'valor':'0', 'x_inf':736, 'x_sup':1536, 'y_inf':1616, 'y_sup':2000},
    {'valor':'ENT', 'x_inf':1536, 'x_sup':2000, 'y_inf':1616, 'y_sup':2000},
    ]
    x=coordenadas[0]
    y=coordenadas[1]
    for tecla in teclas_coords:
        if x>tecla['x_inf'] and x<=tecla['x_sup'] and y>tecla['y_inf']and y <=tecla['y_sup']:
            return tecla['valor']

def pantalla_inicial(borrar=False):
    linea1='ACERQUE'
    linea2='SU TARJETA'
    linea3='AL LECTOR'
    linea4=''
    lineas=[
    {'texto':linea1, 'x':50, 'y':50},
    {'texto':linea2, 'x':25, 'y':100},
    {'texto':linea3, 'x':25, 'y':150},
    {'texto':linea4, 'x':25, 'y':200},
    ]
    if not borrar:
        for linea in lineas:
            display.draw_text(linea['x'],linea['y'] , linea['texto'], font, white_color, black_color)
        display.draw_image('images/maint2_small.raw', x=110, y=300, w=100, h=100)
    if borrar:
        for linea in lineas:
            display.draw_text(linea['x'],linea['y'] , linea['texto'], font, black_color, black_color)
        display.draw_image('images/negro100.raw', x=110, y=300, w=100, h=100)

def pantalla_eleccion(borrar=False):
    # Se usan las variables globales white_color y black_color.
    linea1='ABRIR'
    linea2='UNA'
    linea3='TAQUILLA'
    linea4='CERRAR'
    lineas=[
    {'texto':linea1, 'x':100, 'y':50},
    {'texto':linea2, 'x':120, 'y':100},
    {'texto':linea3, 'x':50, 'y':150},
    {'texto':linea4, 'x':100, 'y':350},
    ]
    display.draw_hline( 0,240,319, white_color)
    if not borrar:
        for linea in lineas:
            display.draw_text(linea['x'],linea['y'] , linea['texto'], font, white_color, black_color)
    if borrar:
        for linea in lineas:
            display.draw_text(linea['x'],linea['y'] , linea['texto'], font, black_color, black_color)

tocado=False
num_introducido='1234'
password='1234'
y_center =25
x_center = 50
pantalla_inicial()
state="start"
gc.collect()

try:
    while True:
        gc.collect() # Recolección de basura en cada iteración del bucle principal
        try:
            if uart.any():
                blink(verde,2,50)
                linea_bytes = uart.readline()
                
                if linea_bytes:
                    mensaje_recibido = linea_bytes.decode('utf-8').strip()
                    if mensaje_recibido:
                    
                        print("Mensaje recibido: ")
                        print(mensaje_recibido)
                    
                    esp_message=mensaje_recibido
                    success = e.send(receiver_mac, esp_message)
                    if success:
                        print("Mensaje enviado con éxito.")
                        blink(azul,2, 50) 
                    else:
                        print("Error al enviar el mensaje.")
                        blink(azul,3, 100)
                    time.sleep(2)

        except:
            continue
        
        if state == "wait_for_PIN":
            time_now=time.ticks_ms()
            time_diff=time.ticks_diff(time_now, inicio_timeout)
            if time_diff >= 3000:
                display.clear(hlines=40)
                gc.collect()
                pantalla_inicial()
                gc.collect()
                state="start"
        
        touch_coords = touch.raw_touch()
        if touch_coords:
##### BLOQUE DE LÓGICA PARA INTERPRETAR LOS TOQUES EN LA PANTALLA #####
            if state == "start":
                state="draw_keyboard"
            if state=="wait_for_PIN":
                print(state)
                print(touch_coords)
                tecla = detectar_valores(touch_coords)
                print(tecla)

                if tecla == 'DEL':
                    long=len(num_introducido)
                    mensaje=''
                    for l in range(long-1):
                        mensaje=mensaje+' '
                    mensaje=mensaje + num_introducido[-1]
                    display.draw_text(x_center, y_center, mensaje, font, black_color, black_color)
                    num_introducido=num_introducido[:-1]
                    text_msg=num_introducido
                
                elif tecla == 'ENT':
                    display.draw_text(x_center, y_center, num_introducido, font, black_color, black_color)
                    if num_introducido==password:
                        text_msg='PIN OK'
                        display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                        time.sleep(0.5)
                        display.draw_text(x_center, y_center,text_msg, font, black_color, black_color)
                        num_introducido=''
                        state="draw_options"
                    else:
                        text_msg='BAD PIN'
                        display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                        time.sleep(0.5)
                        display.draw_text(x_center, y_center, text_msg, font, black_color, black_color)
                        num_introducido=''
                
                elif tecla: # Si es cualquier número
                    num_introducido = num_introducido + tecla
                    text_msg=num_introducido
                
                print('durmiendo')
                time.sleep(0.3)
            
            if state=="choose_action":
                print(touch_coords)
                if touch_coords[1]<950:
                    state="choose_locker"
                    print('elegiste abrir una taquilla')
                    state="start" # Esto parece un bug lógico, debería ir a choose_locker
                else:
                    print('elegiste cerrar')
                    state="close_locker"
                    state="start"
                    display.clear(hlines=40)
                    pantalla_inicial()
                    gc.collect()
                
                    continue
##### BLOQUE DE LÓGICA PARA CONTROLAR QUÉ SE MUESTRA EN PANTALLA #####
        
        if state=="draw_keyboard":
            print('formando teclado')
            display.clear(hlines=40)
            formar_teclado()
            display.draw_text(x_center, y_center ,'PIN CODE', font, white_color, black_color)
            time.sleep(1)
            display.draw_text(x_center, y_center ,'PIN CODE', font, black_color, black_color)
            state="wait_for_PIN"
            inicio_timeout=time.ticks_ms()
            gc.collect()

        if state == "wait_for_PIN":
            display.draw_text(x_center, y_center ,num_introducido, font, white_color, black_color)
            gc.collect()

        if state == "draw_options":
            print('teclado impreso, pin ok')
            display.clear(hlines=40)
            pantalla_eleccion()
            state="choose_action"
            gc.collect()

        if state == "choose_locker":
            print('menú abrir taquilla')
            display.clear(hlines=40)
            formar_teclado()
            display.draw_text(0, 25 ,'CUAL ABRO', font, white_color, black_color)
            time.sleep(1)
            display.draw_text(0, 25 ,'CUAL ABRO', font, black_color, black_color)
            #CIERRE AUTOMÁTICO
            time.sleep(2)
            state="wait_for_locker"
            gc.collect()

except Exception as e:
    print(e)
    try:
        sys.print_exception()
    except:
        machine.soft_reset()
        print('Error. Reiniciando')
