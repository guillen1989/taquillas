import sys
from machine import Pin, SPI
import machine
import time
from xpt2046 import Touch
# Save this file as ili9341.py https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py
from ili9341 import Display, color565
# Save this file as xglcd_font.py https://github.com/rdagger/micropython-ili9341/blob/master/xglcd_font.py
from xglcd_font import XglcdFont
# Set colors
white_color = color565(255, 255, 255)  # white color
black_color = color565(0, 0, 0)        # black color
spi = SPI(1, baudrate=10000000, mosi=Pin(13), miso=Pin(12), sck=Pin(14))
cs = Pin(33, Pin.OUT)
irq = Pin(0, Pin.IN, Pin.PULL_UP)
display = Display(spi, dc=Pin(2), cs=Pin(15), rst=Pin(15),
          width=320, height=480, rotation=0)
touch = Touch(spi, cs=cs, int_pin=irq, int_handler=None)
backlight = Pin(27, Pin.OUT)
backlight.on()
font = XglcdFont('fonts/Dejavu24x43.c', 24, 43)
def formar_teclado(borrar=False):
    white_color = color565(255, 255, 255)  # white color
    black_color = color565(0, 0, 0)        # black color
    font= XglcdFont('fonts/Dejavu24x43.c', 24, 43)
    teclado=[
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
    if not borrar:
        char_color=white_color
    if borrar:
        char_color=black_color
    for line in teclado:
        if line['tipo']=='h':
            display.draw_hline( line['x'],line['y'],line['w'], char_color)
        if line['tipo']=='v':
            display.draw_vline( line['x'],line['y'],line['w'], char_color)
        if line['tipo']!='h'and line['tipo']!='v':
            display.draw_text(line['x'],line['y'] , line['tipo'], font, char_color, black_color)
def detectar_valores(coordenadas):
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
tocado=False
num_introducido='1'
password='1234'
y_center =25
x_center = 50
inicio=True
segunda_pantalla=False
pantalla_inicial()
while True:
    try:
        touch_coords = touch.raw_touch()
        if touch_coords:
            if inicio:
                display.clear(hlines=40)
                formar_teclado()
                inicio=False
            else:
                print(touch_coords)
                time.sleep(0.3)
    except Exception as e:
        sys.print_exception()

'''
# PRUEBAS


        start_time = time.ticks_ms()
        pantalla_inicial()

        end_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(end_time, start_time)
        print(f"El tiempo de ejecución de pantalla_inicial fue: {elapsed_time} ms")
        start_time = time.ticks_ms()
        pantalla_inicial(borrar=True)

        end_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(end_time, start_time)
        print(f"El tiempo de ejecución de borrar pantalla_inicial fue: {elapsed_time} ms")
        start_time = time.ticks_ms()
        display.draw_image('images/inicial.raw', x=0, y=0, w=320, h=480)

        end_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(end_time, start_time)
        print(f"El tiempo de ejecución de imagen fue: {elapsed_time} ms")
        time.sleep(1)

'''
