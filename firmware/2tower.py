# Rui Santos & Sara Santos - Random Nerd Tutorials
# Complete project details at https://RandomNerdTutorials.com/micropython-esp32-bluetooth-low-energy-ble/
import time
from micropython import const
import asyncio
import aioble
import bluetooth
import struct
from machine import Pin
from random import randint

# Init pines
pin3= Pin(3, Pin.OUT)
pin7= Pin(7, Pin.OUT)
pin9= Pin(9, Pin.OUT)
pin20= Pin(20, Pin.OUT)
cerraduras=[
    {'puerta':1, 'pin':pin3},
    {'puerta':2, 'pin':pin7},
    {'puerta':3, 'pin':pin9},
    {'puerta':4, 'pin':pin20},
]
# Init LED
led = Pin(8, Pin.OUT)
led.value(0)

# Init random value
value = 0

# See the following for generating UUIDs:
# https://www.uuidgenerator.net/
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_SENSOR_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
_BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')
# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250

# Register GATT server, the service and characteristics
ble_service = aioble.Service(_BLE_SERVICE_UUID)
sensor_characteristic = aioble.Characteristic(ble_service, _BLE_SENSOR_CHAR_UUID, read=True, notify=True)
led_characteristic = aioble.Characteristic(ble_service, _BLE_LED_UUID, read=True, write=True, notify=True, capture=True)

# Register service(s)
aioble.register_services(ble_service)
async def blink(n_blinks, duration_ms):
    for i in range(n_blinks):
        led.value(0)
        await asyncio.sleep_ms(duration_ms)
        led.value(1)
        await asyncio.sleep_ms(duration_ms)
# Helper to encode the data characteristic UTF-8
def _encode_data(data):
    return str(data).encode('utf-8')

# Helper to decode the LED characteristic encoding (bytes).
def _decode_data(data):
    try:
        if data is not None:
            # Decode the UTF-8 data
            number = int.from_bytes(data, 'big')
            return number
    except Exception as e:
        print("Error decoding message:", e)
        return None

# Get sensor readings
def get_random_value():
    return randint(0,100)
async def comprobation_blink():
    while True:
        led.value(0)
        await asyncio.sleep(1)
        led.value(1)
        await asyncio.sleep(1)
# Serially wait for connections. Don't advertise while a central is connected.
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name="TORRE_2",
                services=[_BLE_SERVICE_UUID],
                ) as connection:
                    print("Connection from", connection.device)
                    await connection.disconnected()             
        except asyncio.CancelledError:
            # Catch the CancelledError
            print("Peripheral task cancelled")
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            # Ensure the loop continues to the next iteration
            await asyncio.sleep_ms(100)

async def wait_for_write():
    while True:
        try:
            print('esperando conexiones')
            connection, data = await led_characteristic.written()
            await asyncio.sleep_ms(0)
            print(data)
            print(type)
            data = _decode_data(data)
            #print('Connection: ', connection)
            #print('Data: ', data)
            await blink(2,100)
            match=False
            for cerradura in cerraduras:
                if cerradura['puerta'] ==data:
                    #activar el pin correspondiente
                    print('Abriendo puerta:')
                    print('puerta: ', cerradura['puerta'])
                    print('pin: ', cerradura['pin'])
                    pin = cerradura['pin']
                    pin.value(1)
                    await asyncio.sleep_ms(0)
                    await asyncio.sleep(2)
                    print('fin de la espera. cerrando puerta')
                    pin.value(0)
                    await asyncio.sleep_ms(0)
                    print('puerta cerrada')
                    await blink(3,100)
                    match=True
                    break
            if match == False:
                print(f'No se ha encontrado una taquilla que coincida con el mensaje recibido: {data}')
            '''
            if data == 1:
                print('Turning LED ON')
                led.value(1)
            elif data == 0:
                print('Turning LED OFF')
                led.value(0)
            else:
                print(data)
                '''
        except asyncio.CancelledError:
            # Catch the CancelledError
            print("Peripheral task cancelled")
        except Exception as e:
            print("Error in peripheral_task:", e)
        finally:
            # Ensure the loop continues to the next iteration
            await asyncio.sleep_ms(100)
            
pines=[pin3,pin7,pin9,pin20]
for pin in pines:
    pin.value(0)

# Init LED
led = Pin(8, Pin.OUT)
led.value(0)
print('arrancando')
async def main():
    t1 =  asyncio.create_task(comprobation_blink())
    t2 = asyncio.create_task(peripheral_task())
    t3 = asyncio.create_task(wait_for_write())
    await asyncio.gather( t2, t3)
try:    
    asyncio.run(main())
except Exception as e:
    print('error: ', e)
    machine.reset()


