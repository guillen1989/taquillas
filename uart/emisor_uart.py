from machine import UART, Pin
import machine
import gc
import time
from mfrc522 import MFRC522
# Se inicializa el LED integrado de la placa ESP32
LED_PIN = 8
led = Pin(LED_PIN, Pin.OUT)
# CONFIGURACIÓN MFRC522
reader = MFRC522(spi_id=0,sck=6,miso=5,mosi=4,cs=7,rst=10)
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
blink(5,100)

# Asignación de Pines
# Usamos UART 2 por ser el más libre (configurable en cualquier GPIO)
# ¡Asegúrate de que estos pines GPIO estén conectados correctamente!
UART_ID = 1
TX_PIN = 3  # PIN DUMMY. ANTES ERA EL 10 PERO CAUSA CONFLICTO CON EL RST DEL RFID. Conectar al pin RX de la Placa B
#TX_PIN = 10  # Conectar al pin RX de la Placa B
RX_PIN = 1  # Conectar al pin TX de la Placa B

# Configuración del UART
# baudrate debe ser el mismo en ambas placas
uart = UART(UART_ID, baudrate=115200, tx=Pin(TX_PIN), rx=Pin(RX_PIN))
print('uart funcionando')

contador = 0

#print("UART Transmisor iniciado.")

while True:
    reader.init()
    print('reader funcionando')
    (stat, tag_type) = reader.request(reader.REQIDL)
    mensaje = "Hola desde ESP32 A. Mensaje #{}".format(contador)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()

        print(uid)
        tarjeta_leida=reader.tohexstring(uid)
        #print(type(tarjeta_leida))
        mensaje=tarjeta_leida
    # El método write() espera bytes, por lo que codificamos el string.
    # El '\n' (salto de línea) ayuda a la Placa B a saber cuándo termina el mensaje.
        #print(len(mensaje))
        if len(mensaje)==24:
            #print("leído correcto, longitud 24")
            print(mensaje)
            uart.write(mensaje.encode('utf-8') + b'\n')
            print("Mensaje enviado:", mensaje)
        contador += 1
        blink(1,50)
        #reader._tocard(PICC_HALT_A, [0, 0], 1)
        reader.reset()
        time.sleep(2)
        #gc.collect()
    else:
        time.sleep(0.3)
