from machine import Pin, SPI
import time
from xpt2046 import Touch
# Save this file as ili9341.py https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py
from ili9341 import Display, color565
# Save this file as xglcd_font.py https://github.com/rdagger/micropython-ili9341/blob/master/xglcd_font.py
from xglcd_font import XglcdFont
# Set colors
white_color = color565(255, 255, 255)  # white color
black_color = color565(0, 0, 0)        # black color
spi = SPI(1, baudrate=1000000, mosi=Pin(13), miso=Pin(12), sck=Pin(14))
cs = Pin(33, Pin.OUT)
irq = Pin(0, Pin.IN, Pin.PULL_UP)
display = Display(spi, dc=Pin(2), cs=Pin(15), rst=Pin(15),
          width=480, height=320, rotation=90)
touch = Touch(spi, cs=cs, int_pin=irq, int_handler=None)
backlight = Pin(27, Pin.OUT)
backlight.on()
display.clear(black_color)

unispace_font = XglcdFont('fonts/Unispace12x24.c', 12, 24)
    

tocado=False
while True:
    if not tocado:
        try:
#             display.clear(black_color)
            font_size_w = unispace_font.width
            font_size_h = unispace_font.height
            text_msg = 'TOUCH ME'
            x_center = int((display.width-len(text_msg)*font_size_w)/2)
            y_center = int(((display.height)/2)-(font_size_h/2))
            display.draw_text(x_center, y_center, text_msg, unispace_font, black_color, white_color)
            touch_coords = touch.raw_touch()
#             print(touch_coords)
            if touch_coords:
                print("\n¡Éxito! Pines encontrados.")
                print(f"Coordenadas leídas: {touch_coords}")
    #             text_msg = 'TOCADO'
    #             x_center = int((display.width-len(text_msg)*font_size_w)/2)
    #             y_center = int(((display.height)/2)-(font_size_h/2))
    #             display.clear(black_color)
    #             display.draw_text(x_center, y_center, text_msg, unispace_font, black_color, white_color)
                tocado=True
                time.sleep_ms(50)
                
            
            
                
        except Exception as e:
            print(e)
            print(f"Error al probar esta combinación: {e}")
        if tocado:
            display.clear(white_color)
            text_msg = 'TOCADO'
            x_center = int((display.width-len(text_msg)*font_size_w)/2)
            y_center = int(((display.height)/2)-(font_size_h/2))
            
            display.draw_text(x_center, y_center, text_msg, unispace_font, white_color, black_color)
            print('segunda pantalla')
            
            print('esperando segundo toque')
            touch = Touch(spi, cs=cs, int_pin=irq, int_handler=None)
            touch_coords_2 = touch.raw_touch()
#             print(type(touch_coords_2))
            
            tocado=False
    
                
            

