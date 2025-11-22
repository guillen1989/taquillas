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
touch = Touch(spi, cs=cs, int_pin=irq, int_handler=None,
             width=320, height=480)
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
def pantalla_eleccion(borrar=False):
    white_color = color565(255, 255, 255)  # white color
    black_color = color565(0, 0, 0)        # black color
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
inicio=True
teclado_impreso=False
pin_ok=False
eligiendo=False
abrir_taquilla=False
try:
    while True:
        touch_coords = touch.raw_touch()
        if touch_coords:
            if inicio:
                inicio=False
            if not inicio and teclado_impreso:
                print(touch_coords)
                print(detectar_valores(touch_coords))
                if detectar_valores(touch_coords) == 'DEL':
                    long=len(num_introducido)
                    mensaje=''
                    for l in range(long-1):
                        mensaje=mensaje+' '
                    mensaje=mensaje + num_introducido[-1]
                    display.draw_text(x_center, y_center, mensaje, font, black_color, black_color)
                    num_introducido=num_introducido[:-1]
                    text_msg=num_introducido
                if detectar_valores(touch_coords) == 'ENT':
                    display.draw_text(x_center, y_center, num_introducido, font, black_color, black_color)
                    if num_introducido==password:
                        text_msg='PIN OK'
                        display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                        time.sleep(0.5)
                        display.draw_text(x_center, y_center,text_msg, font, black_color, black_color)
                        num_introducido=''
                        pin_ok=True
                    else:
                        text_msg='BAD PIN'
                        display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                        time.sleep(0.5)
                        display.draw_text(x_center, y_center, text_msg, font, black_color, black_color)
                        num_introducido=''

                if detectar_valores(touch_coords) != 'DEL'and detectar_valores(touch_coords)!='ENT':
                    num_introducido = num_introducido + detectar_valores(touch_coords)
                    text_msg=num_introducido
                print('durmiendo')
                time.sleep(0.3)
            if pin_ok and eligiendo:
                print(touch_coords)
                if touch_coords[1]<950:
                    abrir_taquilla=True
                    print('elegiste abrir una taquilla')
                else:
                    print('elegiste cerrar')
                    inicio=True
                    teclado_impreso=False
                    pin_ok=False
                    eligiendo=False
                    abrir_taquilla=False
                    display.clear(hlines=40)
                    pantalla_inicial()
                    continue
        if not inicio and not teclado_impreso and not pin_ok:
            print('formando teclado')
            display.clear(hlines=40)
            formar_teclado()
            display.draw_text(x_center, y_center ,'PIN CODE', font, white_color, black_color)
            time.sleep(1)
            display.draw_text(x_center, y_center ,'PIN CODE', font, black_color, black_color)
            teclado_impreso=True
        if not inicio and teclado_impreso and not pin_ok:
            print('not inicio and teclado impreso and not pin_ok')
            display.draw_text(x_center, y_center ,num_introducido, font, white_color, black_color)
        if teclado_impreso and pin_ok and not abrir_taquilla:
            print('teclado impreso, pin ok')
            display.clear(hlines=40)
            pantalla_eleccion()
            teclado_impreso=False
            eligiendo=True
        if abrir_taquilla and not teclado_impreso:
            print('menú abrir taquilla')
            display.clear(hlines=40)
            formar_teclado()
            display.draw_text(0, 25 ,'CUAL ABRO', font, white_color, black_color)
            time.sleep(1)
            display.draw_text(0, 25 ,'CUAL ABRO', font, black_color, black_color)
            teclado_impreso=True
            eligiendo=False
            #CIERRE AUTOMÁTICO
            time.sleep(2)
            inicio=True
            teclado_impreso=False
            pin_ok=False
            eligiendo=False
            abrir_taquilla=False
            display.clear(hlines=40)
            pantalla_inicial()

except Exception as e:
    print(e)
    try:
        sys.print_exception()
    except:
        machine.soft_reset()
        print('reiniciando')

