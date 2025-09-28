from machine import UART, Pin
import time
# Se inicializa el LED integrado de la placa ESP32
LED_PIN = 8
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
blink(5,100)

# Asignación de Pines
# Usamos UART 2 por ser el más libre (configurable en cualquier GPIO)
# ¡Asegúrate de que estos pines GPIO estén conectados correctamente!
UART_ID = 1
TX_PIN = 20  # Conectar al pin RX de la Placa B
RX_PIN = 21  # Conectar al pin TX de la Placa B

# Configuración del UART
# baudrate debe ser el mismo en ambas placas
uart = UART(UART_ID, baudrate=115200, tx=Pin(TX_PIN), rx=Pin(RX_PIN))

contador = 0

print("UART Transmisor iniciado.")

while True:
    mensaje = "Hola desde ESP32 A. Mensaje #{}".format(contador)
    # El método write() espera bytes, por lo que codificamos el string.
    # El '\n' (salto de línea) ayuda a la Placa B a saber cuándo termina el mensaje.
    uart.write(mensaje.encode('utf-8') + b'\n')
    print("Mensaje enviado:", mensaje)
    contador += 1
    blink(1,50)
    time.sleep(2)
