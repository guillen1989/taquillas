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
# Deben coincidir con la Placa A
UART_ID = 1
TX_PIN = 21  # Conectar al pin RX de la Placa A
RX_PIN = 20  # Conectar al pin TX de la Placa A

# Configuración del UART
# baudrate debe ser el mismo en ambas placas
uart = UART(UART_ID, baudrate=115200, tx=Pin(TX_PIN), rx=Pin(RX_PIN))

print("UART Receptor iniciado. Esperando datos...")

while True:
    # Chequea si hay datos disponibles para leer
    if uart.any():
        # Lee la línea completa hasta el salto de línea ('\n')
        # El timeout es para no esperar indefinidamente si el mensaje es incompleto.
        linea_bytes = uart.readline()
        
        if linea_bytes:
            # Decodifica los bytes a un string (MicroPython trabaja con bytes)
            mensaje_recibido = linea_bytes.decode('utf-8').strip()
            
            print("Datos recibidos:", mensaje_recibido)
            blink(2,50)

    time.sleep_ms(100) # Pequeña pausa para no saturar el CPU
