# torre2.py - BLUETOOTH LOW ENERGY PERIFÉRICO (SERVIDOR) para Torre 2
# Lógica LED: Par enciende (ON), Impar apaga (OFF).

from micropython import const
import asyncio
import aioble
import bluetooth
import struct
from machine import Pin
from random import randint

# Init LED
# Asegúrate de usar el pin correcto para tu placa (ejemplo: Pin(8))
LED_PIN = 8 
led = Pin(LED_PIN, Pin.OUT)
led.value(0) # LED apagado por defecto

# --- UUIDs (DEBEN COINCIDIR con madre.py) ---
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_SENSOR_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
_BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')

# Nombre de publicidad para la Torre 2
ADVERTISEMENT_NAME = "ESP32_T2" 
_ADV_INTERVAL_MS = 250_000

# --- Registro del Servidor GATT ---
ble_service = aioble.Service(_BLE_SERVICE_UUID)
# Característica del sensor (mantenida por consistencia, no usada aquí)
sensor_characteristic = aioble.Characteristic(ble_service, _BLE_SENSOR_CHAR_UUID, read=True, notify=True)
# Característica del LED (escritura)
led_characteristic = aioble.Characteristic(ble_service, _BLE_LED_UUID, read=True, write=True, notify=True, capture=True)

aioble.register_services(ble_service)

# --- Funciones Auxiliares ---

# Helper to decode the LED characteristic encoding (bytes).
def _decode_data(data):
    """Decodifica el byte recibido a un entero."""
    try:
        if data is not None:
            # Asume que el cliente envía un byte simple (struct.pack('<b', command))
            number = int.from_bytes(data, 'big') 
            return number
    except Exception as e:
        print(f"Error decodificando el dato: {e}")
        return None

# --- Tareas Asíncronas ---

async def peripheral_task():
    """Tarea de publicidad y espera de conexión."""
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name=ADVERTISEMENT_NAME,
                services=[_BLE_SERVICE_UUID],
                ) as connection:
                    print(f"Connection from {connection.device}")
                    # Esperar a que la conexión se pierda
                    await connection.disconnected()
                    print("Disconnected.")          
        except asyncio.CancelledError:
            print("Peripheral task cancelled")
            break
        except Exception as e:
            print(f"Error in peripheral_task: {e}")
        finally:
            await asyncio.sleep_ms(100)

async def wait_for_write():
    """Tarea que espera la escritura en la característica del LED."""
    while True:
        try:
            # Esperar a que se escriba un valor
            connection, data = await led_characteristic.written()
            
            # Decodificar el valor
            value = _decode_data(data)
            
            if value is not None:
                print(f'-> COMANDO RECIBIDO: Valor = {value}')
                
                # Lógica Específica de la Torre 2: Par enciende, Impar apaga
                if value % 2 == 0:
                    print('   -> Turning LED ON (Valor Par)')
                    led.value(1)
                else:
                    print('   -> Turning LED OFF (Valor Impar)')
                    led.value(0)
            
        except asyncio.CancelledError:
            print("Write task cancelled")
            break
        except Exception as e:
            print(f"Error in write task: {e}")
        finally:
            await asyncio.sleep_ms(100)
            
# --- Ejecución Principal ---
async def main():
    t_peripheral = asyncio.create_task(peripheral_task())
    t_write = asyncio.create_task(wait_for_write())
    await asyncio.gather(t_peripheral, t_write) # Esperar a ambas tareas
print('arrancando')
asyncio.run(main())
