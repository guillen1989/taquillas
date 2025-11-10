# BLUETOOTH LOW ENERGY BROADCASTER (PERIFÉRICO - PLACA MADRE)
# Implementa Stop-and-Wait con:
# 1. Límite de 5 reintentos por número.
# 2. Pausa de 2 segundos DESPUÉS de recibir el ACK.
# 3. NO pausa de 2 segundos si se supera el límite de reintentos.

from micropython import const
import asyncio
import aioble
import bluetooth
from machine import Pin
from random import randrange
import time
import struct

# Init LED (Pin 2)
led = Pin(2, Pin.OUT)
led.value(0)

# --- Constantes BLE ---
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_ACK_CHAR_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')

# Intervalo de publicidad y duración de cada ciclo de publicidad
_ADV_INTERVAL_US = 500_000 # 500ms
_ADV_DURATION_MS = 1000 # Duración de la publicidad (1 segundo)
_RETRY_DELAY_MS = 500 # Pausa entre reintentos fallidos
_MAX_ATTEMPTS = 5 # Límite de intentos de publicidad
_SUCCESS_DELAY_S = 2 # Pausa tras recibir el ACK

# --- Estado Global Compartido para Sincronización ---
ack_received_event = asyncio.Event() 
current_value_to_ack = 0

# --- GATT Setup (Solo para recibir ACK) ---
ack_service = aioble.Service(_BLE_SERVICE_UUID)
ack_characteristic = aioble.Characteristic(
    ack_service, _BLE_ACK_CHAR_UUID, write=True, capture=True
)
aioble.register_services(ack_service)


# --- Tarea: Parpadeo de LED ---
async def blink_led(num_blinks=2, delay_ms=100):
    """Hace parpadear el LED dos veces para confirmar la recepción del ACK."""
    for _ in range(num_blinks):
        led.value(1)
        await asyncio.sleep_ms(delay_ms)
        led.value(0)
        await asyncio.sleep_ms(delay_ms)

async def wait_for_write():
    """Espera la escritura del mensaje ACK y verifica el valor."""
    global current_value_to_ack
    global ack_received_event

    # print("Iniciando tarea de escucha de ACK...")
    while True:
        try:
            # wait_for_write es bloqueante y espera por una conexión y escritura.
            connection, data = await ack_characteristic.written()
            
            print('Conexión establecida momentáneamente por:', connection.device)
            print(f'Datos recibidos (bytes): {data}')
            
            if len(data) > 1:
                try:
                    command_str = data.decode('utf-8').strip()
                    if command_str.startswith('ACK'):
                        original_value_str = command_str[3:].strip()
                        
                        try:
                            original_value = int(original_value_str)
                            
                            # ** VERIFICACIÓN CRÍTICA DEL ACK **
                            if original_value == current_value_to_ack:
                                print(f'*** ÉXITO: ACK VERIFICADO para valor: {original_value}. Pausa de {_SUCCESS_DELAY_S}s a continuación. ***')
                                asyncio.create_task(blink_led())
                                ack_received_event.set() 
                            else:
                                print(f'--- ALERTA: ACK ({original_value}) NO coincide con el valor esperado ({current_value_to_ack}). IGNORANDO. ---')
                            
                        except ValueError:
                            print(f"Error: El valor ACK '{original_value_str}' no es un número válido.")
                        
                    # else: # No es necesario imprimir si el comando no es ACK, pero se podría dejar.
                    #     print(f'Comando de escritura string desconocido: {command_str}')

                except UnicodeDecodeError:
                    print(f"Error: No se pudo decodificar la escritura como cadena UTF-8: {data}")
            
        except asyncio.CancelledError:
            print("Tarea wait_for_write cancelada.")
            break
        except Exception as e:
            print(f"Error al procesar la escritura: {e}")
            break

async def advertising_task():
    """
    Genera un valor, lo publicita con un límite de reintentos y aplica una pausa
    condicional según el resultado.
    """
    global current_value_to_ack
    global ack_received_event
    
    print("Iniciando tarea de publicidad (Broadcaster) en modo Stop-and-Wait...")
    while True:
        # 1. Generar nuevo valor y establecer el estado
        value = randrange(1, 9, 1)
        current_value_to_ack = value
        ack_received_event.clear()
        
        attempt_count = 0 # Contador de intentos para el número actual
        
        print(f'\n*** NUEVO CICLO: Enviando valor {value}. Máximo de {_MAX_ATTEMPTS} intentos. ***')
        
        # Bucle de publicidad del mismo valor hasta que se reciba el ACK o se agoten los intentos
        while not ack_received_event.is_set() and attempt_count < _MAX_ATTEMPTS:
            attempt_count += 1
            value_str = str(value)
            mfg_data = struct.pack('<b', value)

            print(f'Publicitando valor: {value}. Intento {attempt_count}/{_MAX_ATTEMPTS}...')
            
            try:
                # Iniciar la publicidad de forma CONECTABLE con un timeout de 1 segundo.
                await aioble.advertise(
                    _ADV_INTERVAL_US,
                    name=f"ESP32-V{value_str}",
                    services=[_BLE_SERVICE_UUID],
                    manufacturer=(0xFFFF, mfg_data),
                    connectable=True,
                    timeout_ms=_ADV_DURATION_MS 
                )
                # Si llega aquí sin excepción, hubo conexión (el ACK podría estar por llegar)
            except asyncio.TimeoutError:
                pass # El timeout es esperado, no cuenta como fallo de envío, pero continuamos el ciclo
            except Exception as e:
                print(f"Error durante la publicidad: {e}")
                
            # Si el ACK no se ha recibido, hacemos una pequeña pausa antes de re-publicitar.
            if not ack_received_event.is_set() and attempt_count < _MAX_ATTEMPTS:
                 await asyncio.sleep_ms(_RETRY_DELAY_MS) # Pausa corta entre reintentos.
            
        
        # 3. Lógica Post-Ciclo (Pausa Condicional)
        if ack_received_event.is_set():
            # A. Éxito: ACK recibido dentro del límite. Aplicar pausa de 2 segundos.
            print(f'ACK para {value} recibido. Iniciando pausa obligatoria de {_SUCCESS_DELAY_S} segundos.')
            await asyncio.sleep(_SUCCESS_DELAY_S) 
        else:
            # B. Fallo: Límite de intentos superado. NO aplicar pausa.
            print(f'!!! LÍMITE DE REINTENTOS SUPERADO ({_MAX_ATTEMPTS}). Saltando valor {value}. NO ESPERA DE 2S. !!!')

        # Pequeña pausa de control entre ciclos antes de generar el nuevo número.
        await asyncio.sleep_ms(100) 

async def main():
    t_adv = asyncio.create_task(advertising_task())
    t_write = asyncio.create_task(wait_for_write())
    await asyncio.gather(t_adv, t_write)

while True:
    try:
        print("Iniciando ciclo principal del Broadcaster (MicroPython)...")
        asyncio.run(main())
    except Exception as e:
        print(f"Error en el bucle principal: {e}")
    time.sleep(1)
