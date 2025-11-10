# BLUETOOTH LOW ENERGY CENTRAL SCANNER (TORRE 2)
# Rango de interés: Valores del 5 al 8.
# LED: Pin 8 con lógica de parpadeo según el estado de la señal/ACK.

import asyncio
import aioble
import bluetooth
from micropython import const
from time import sleep_ms
from machine import Pin 
import struct

# Init LED en PIN 8 (Ajustado según tu solicitud)
led = Pin(8, Pin.OUT)
led.value(0)

# --- UUIDs (DEBEN COINCIDIR con la Placa Madre) ---
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_ACK_CHAR_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')

# Prefijo del dispositivo periférico que estamos buscando
TARGET_DEVICE_NAME = "ESP32-V"

# --- Rango de Valores para la Torre 1 ---
MIN_VALUE = 5
MAX_VALUE = 8

# --- Tareas Auxiliares ---

async def blink_led_local(num_blinks=2, delay_ms=100):
    """Hace parpadear el LED local para confirmación."""
    for _ in range(num_blinks):
        led.value(1) # Encender
        await asyncio.sleep_ms(delay_ms)
        led.value(0) # Apagar
        await asyncio.sleep_ms(delay_ms)

def extract_value_from_name(device_name):
    """Extrae el valor numérico del nombre del dispositivo, e.g., 'ESP32-V2' -> 2."""
    if device_name and device_name.startswith(TARGET_DEVICE_NAME):
        try:
            value = int(device_name[-1])
            return value
        except ValueError:
            return None
    return None

async def send_ack(device, current_value):
    """
    Gestiona la conexión, la escritura del ACK y la desconexión.
    Llamará a 'blink_led_local(2)' en caso de éxito.
    """
    response_msg = f"ACK{current_value}"
    command = response_msg.encode('utf-8')
    
    print(f"-> Valor {current_value} detectado. Conectando para enviar ACK...")

    connection = None
    try:
        # 1. CONECTAR
        connection = await device.connect(timeout_ms=3000)
        
        # 2. DESCUBRIR SERVICIO Y CARACTERÍSTICA
        async with connection:
            service = await connection.service(_BLE_SERVICE_UUID)
            ack_char = await service.characteristic(_BLE_ACK_CHAR_UUID)
            
            # 3. ESCRIBIR ACK
            await ack_char.write(command, response=False)
            
            # 4. CONFIRMACIÓN Y DESCONEXIÓN
            print(f"*** ÉXITO: ACK enviado ({response_msg}). Desconectando... ***")
            # DOS PARPADEOS: Éxito
            asyncio.create_task(blink_led_local(num_blinks=2))
        
    except asyncio.TimeoutError:
        print("!!! FALLO: Tiempo de espera agotado al intentar conectar/escribir.")
    except Exception as e:
        print(f"!!! FALLO: Error al escribir o desconectar: {e}")
    finally:
        # 5. ASEGURAR DESCONEXIÓN
        if connection and connection.is_connected():
            await connection.disconnect()

# --- Tarea Principal Central ---

async def central_task():
    print(f"Iniciando Tarea Central (Torre 1). Rango activo: {MIN_VALUE} a {MAX_VALUE}. LED en Pin 8.")
    while True:
        try:
            print(f"\nEscaneando paquetes de publicidad...")
            
            # Escaneo con un timeout de 5 segundos
            async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
                async for res in scanner:
                    device_name = res.name()
                    
                    if device_name and device_name.startswith(TARGET_DEVICE_NAME):
                        
                        current_value = extract_value_from_name(device_name)
                        
                        if current_value is not None:
                            # LÓGICA DE FILTRADO DE RANGO (1 a 4)
                            if MIN_VALUE <= current_value <= MAX_VALUE:
                                
                                # EN RANGO: PROCEDER A CONEXIÓN Y ACK
                                print(f"-> Placa Madre detectada con valor {current_value} (EN RANGO).")
                                await send_ack(res.device, current_value)
                                
                                # Detener el escaneo temporalmente después de una acción exitosa
                                break
                            else:
                                # FUERA DE RANGO: SOLO PARPADEAR
                                print(f"-> Placa Madre detectada con valor {current_value} (FUERA DE RANGO).")
                                # UN PARPADEO: Detectado, pero no se requiere acción
                                asyncio.create_task(blink_led_local(num_blinks=1)) 

        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            print("Tarea principal cancelada.")
            break
        except Exception as e:
            print(f"Error inesperado en central_task: {e}")
            await asyncio.sleep(1) 


# --- Ejecución Principal ---
asyncio.run(central_task())
