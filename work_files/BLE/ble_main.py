# madre.py - BLUETOOTH LOW ENERGY CENTRAL (CLIENT)
# Ahora configurado para conectarse a Torre 1 (ESP32) o Torre 2 (ESP32_T2)

import asyncio
import aioble
import bluetooth
import struct
import random
from micropython import const
from time import sleep_ms

# --- UUIDs del Servidor Periférico (DEBEN COINCIDIR) ---
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')

# Nombres de los dispositivos periféricos
TARGET_DEVICE_T1 = "ESP32"      # Torre 1: 0/1 -> OFF/ON
TARGET_DEVICE_T2 = "ESP32_T2"   # Torre 2: Par/Impar -> ON/OFF

# --- Tareas Auxiliares ---

def _encode_led_command(command):
    """Codifica el comando como un byte para enviarlo."""
    # El periférico espera un byte (e.g., b'\x00', b'\x01', etc.)
    return struct.pack('<b', command)


async def connect_and_send_command(target_name, command_value):
    """
    Función reutilizable para escanear, conectar, enviar el comando y desconectar.
    """
    print(f"\nEscaneando... Buscando '{target_name}' para enviar comando {command_value}")
    
    device = None
    try:
        # 1. ESCANEO: Buscar el dispositivo objetivo
        async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
            async for res in scanner:
                if res.name() == target_name:
                    print(f"¡Dispositivo encontrado! Dirección: {res.device.addr_hex()}")
                    device = res.device
                    break

        if not device:
            print(f"Dispositivo '{target_name}' no encontrado. Reintentando...")
            return

        # 2. CONEXIÓN
        print(f"Intentando conectar a {target_name}...")
        connection = await device.connect()
        print("¡Conectado!")

        # 3. DESCUBRIMIENTO DE SERVICIOS Y CARACTERÍSTICAS
        async with connection:
            print("Buscando servicio y característica LED...")
            service = await connection.service(_BLE_SERVICE_UUID)
            led_char = await service.characteristic(_BLE_LED_UUID)

            # 4. INTERACCIÓN (Envío de Comando)
            command = _encode_led_command(command_value)
            
            try:
                # Escribir el valor
                await led_char.write(command, response=False)
                print(f"-> COMANDO ENVIADO a {target_name}: Valor = {command_value}")
            except Exception as e:
                print(f"Error al escribir en la característica del LED de {target_name}: {e}")
            
            # El 'async with connection:' se encarga de la desconexión al salir

    except Exception as e:
        print(f"Error inesperado en connect_and_send_command para {target_name}: {e}")


# --- Tarea Principal Central ---

async def central_task():
    print("Iniciando tarea Central (Cliente) BLE...")
    while True:
        try:
            # 1. Generar Valor Aleatorio (0, 1, 2, o 3)
            # 0 y 1 van a Torre 1; 2 y 3 van a Torre 2
            random_value = random.randint(0, 3)
            
            target_device = None
            
            if random_value in (0, 1):
                # Caso Torre 1: 0 (OFF) o 1 (ON)
                target_device = TARGET_DEVICE_T1
                command_to_send = random_value
                
            elif random_value in (2, 3):
                # Caso Torre 2: 2 (Par) o 3 (Impar)
                target_device = TARGET_DEVICE_T2
                command_to_send = random_value
                
            print(f"\n*** Valor Aleatorio Generado: {random_value} ***")
            
            # 2. Ejecutar Conexión y Envío
            if target_device:
                await connect_and_send_command(target_device, command_to_send)
                
            # Esperar 2 segundos antes de la próxima iteración
            await asyncio.sleep(2)

        except asyncio.CancelledError:
            print("Tarea principal cancelada.")
            break
        except Exception as e:
            print(f"Error inesperado en central_task: {e}")
            await asyncio.sleep(2) # Pausa antes de reintentar


# --- Ejecución Principal ---
asyncio.run(central_task())
