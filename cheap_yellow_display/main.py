import network
import gc
import json
# import espnow # Ya no necesario
import sys
from machine import Pin, SPI, UART
import machine
import time
from xpt2046 import Touch
from ili9341 import Display, color565
from xglcd_font import XglcdFont

# --- BLE IMPORTS ---
import asyncio
import aioble
import bluetooth
import struct
# --- FIN BLE IMPORTS ---

gc.collect() # Recolección inicial

# 🎨 VARIABLES GLOBALES DE PANTALLA (Creadas una única vez)
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
# Objeto de fuente creado UNA SOLA VEZ
font = XglcdFont('fonts/Dejavu24x43.c', 24, 43)

# ⌨️ ESTRUCTURA DEL TECLADO
TECLADO_COORDS = [
    # ... (El resto de TECLADO_COORDS sigue igual)
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

# --- BLE / UUIDS / TARGETS ---
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_LED_UUID = bluetooth.UUID('19b10002-e8f2-537e-4f6c-d104768a1214')

# Mapeo de Torre a Nombre BLE
TOWER_MAC_MAP = {
    1: "TORRE_1",    # Torre 1: Usada por 1torre.py
    2: "TORRE_2", # Torre 2: Usada por torre2.py
    # Puedes añadir más torres si lo necesitas:
    # 3: "ESP32_T3", 
    # 4: "ESP32_T4", 
    # 5: "ESP32_T5", 
}
# --- FIN BLE/UUIDS/TARGETS ---


# 🗑️ CONFIGURACIÓN Y ARRANQUE (Limpieza de ESP NOW/WiFi para BLE)
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()
# No se inicializa ESP Now

rojo =4
verde =17
azul =16

# VARIABLES UART (Para el lector de tarjetas)
UART_ID = 1
TX_PIN = 22
RX_PIN = 21

# Configuración del UART
try:
    uart = UART(UART_ID, baudrate=115200, tx=Pin(TX_PIN), rx=Pin(RX_PIN))
    print("UART Receptor iniciado. Esperando datos...")
except:
    print("Error activando UART")

# Se definen las funciones para controlar el LED
def blink(led,times, duration):
    """Hace parpadear el LED un número de veces con una duración específica."""
    led = Pin(led, Pin.OUT)
    for _ in range(times):
        led.value(0)
        time.sleep_ms(duration)
        led.value(1)
        time.sleep_ms(duration)

blink(verde,5,100) # Blink inicial

# --- Funciones Auxiliares de Pantalla y Teclado (SIN MODIFICAR) ---
def formar_teclado(borrar=False):
    # ... (Cuerpo de la función igual)
    if not borrar:
        char_color=white_color
    if borrar:
        char_color=black_color
    for line in TECLADO_COORDS:
        if line['tipo']=='h':
            display.draw_hline( line['x'],line['y'],line['w'], char_color)
        if line['tipo']=='v':
            display.draw_vline( line['x'],line['y'],line['w'], char_color)
        if line['tipo']!='h'and line['tipo']!='v':
            display.draw_text(line['x'],line['y'] , line['tipo'], font, char_color, black_color)

def detectar_valores(coordenadas):
    # ... (Cuerpo de la función igual)
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
    # ... (Cuerpo de la función igual)
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
    # ... (Cuerpo de la función igual)
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

def opening_locker_screen(borrar=False,taquilla='111'):
    # ... (Cuerpo de la función igual)
    linea1=''
    linea2='ABRIENDO'
    linea3='TAQUILLA'
    linea4= taquilla
    lineas=[
    {'texto':linea1, 'x':100, 'y':50},
    {'texto':linea2, 'x':50, 'y':100},
    {'texto':linea3, 'x':50, 'y':150},
    {'texto':linea4, 'x':100, 'y':350},
    ]
    #display.draw_hline( 0,240,319, white_color)
    if not borrar:
        for linea in lineas:
            display.draw_text(linea['x'],linea['y'] , linea['texto'], font, white_color, black_color)
    if borrar:
        for linea in lineas:
            display.draw_text(linea['x'],linea['y'] , linea['texto'], font, black_color, black_color)

# --- Fin Funciones Auxiliares de Pantalla y Teclado ---


# 📡 FUNCIÓN ASÍNCRONA DE COMUNICACIÓN BLE (Adaptada de madre.py)
def _encode_command_to_byte(message):
    """Convierte un mensaje de taquilla ('ocupar1' o 'liberar1') a un byte de comando."""
    # El periférico espera un byte. Podemos usar el número de taquilla como el valor a enviar.
    # El periférico 1torre.py solo mira si es 0 (liberar/OFF) o 1 (ocupar/ON).
    # El periférico torre2.py mira la paridad. 
    # Aquí el taquillero es el cliente y necesitamos enviar el número de taquilla.
    
    # Extraer el número de la taquilla del mensaje (ej. 'ocupar1' -> 1)
    try:
        command_value = int(message.strip('ocupar').strip('liberar'))
    except ValueError:
        command_value = 0 # Valor por defecto si falla
    
    # Codificar el valor como un byte
    return struct.pack('<b', command_value)
async def send_command_via_ble(target_tower_id, message_type, locker_name):
    """
    Escanea, conecta y envía un comando BLE a la torre correcta.
    message_type: 'ocupar' o 'liberar'
    locker_name: número de la taquilla (ej. '1', '4')
    """
    target_name = TOWER_MAC_MAP.get(target_tower_id)
    if not target_name:
        print(f"Error: Torre {target_tower_id} no mapeada a un nombre BLE.")
        return False

    print(f"\nBLE: Buscando '{target_name}' para enviar '{message_type + locker_name}'")

    device = None
    try:
        # 1. ESCANEO (3 segundos)
        async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
            async for res in scanner:
                if res.name() == target_name:
                    device = res.device
                    print(f"BLE: Dispositivo '{target_name}' encontrado.")
                    break

        if not device:
            print(f"BLE: Dispositivo '{target_name}' no encontrado.")
            return False # Evita crash si no se encuentra el dispositivo

        # 2. CONEXIÓN
        connection = await device.connect()
        print("BLE: ¡Conectado!")

        # 3. DESCUBRIMIENTO DE SERVICIOS Y CARACTERÍSTICAS
        async with connection:
            service = await connection.service(_BLE_SERVICE_UUID)
            if not service:
                print(f"BLE: Error: Servicio {_BLE_SERVICE_UUID} no encontrado en {target_name}.")
                return False # Evita crash si no se encuentra el servicio

            led_char = await service.characteristic(_BLE_LED_UUID)
            if not led_char:
                print(f"BLE: Error: Característica {_BLE_LED_UUID} no encontrada en {target_name}.")
                return False # Evita crash si no se encuentra la característica

            # 4. INTERACCIÓN (Envío de Comando)
            command = _encode_command_to_byte(message_type + locker_name)

            try:
                # Escribir el valor
                await led_char.write(command, response=True)
                print(f"BLE: Comando '{message_type + locker_name}' enviado a {target_name}.")
                return True
            except Exception as e:
                print(f"BLE: Error al escribir en característica de {target_name}: {e}")
                return False

    except Exception as e:
        print(f"BLE: Error en la comunicación con {target_name}: {e}")
        return False
    # El 'async with connection:' se encarga de la desconexión al salir
# -- GESTIÓN DE PERSISTENCIA (ARCHIVO JSON) --
# ... (Bloque de persistencia igual)
try:
    g=open("persistencia", "r")
    data=json.load(g)
    print("json abierto")
    g.close()
except:
    print("json no disponible. Creando archivo...")
    f=open("persistencia", "w")
    # Aseguramos que haya taquillas en la Torre 1 y Torre 2 para el ejemplo
    taquillas=[
        {'nombre':'1', 'torre': 2, 'GPIO' : 5,'tarjeta': '',"fecha_inicio":0},
        {'nombre':'2','torre': 2, 'GPIO' : 6,'tarjeta': "","fecha_inicio":0},
        {'nombre':'3','torre': 2, 'GPIO' : 7,'tarjeta': "","fecha_inicio":0}, # Taquilla 3 en Torre 2
        {'nombre':'4','torre': 2, 'GPIO' : 9,'tarjeta': "","fecha_inicio":0} # Taquilla 4 en Torre 2
    ]
    f.write(json.dumps(taquillas))
    f.close()
    data = taquillas # Cargar datos después de crear
# --- Fin Persistencia ---

# --- Inicialización de Variables Globales (igual) ---
num_introducido='1234'
locker_n=''
password='1234'
y_center =25
x_center = 50
pantalla_inicial()
state="start"

# Declarar variables que se usan en la lógica de UART/Touch
# Se inicializan a None para que el bucle principal las use
taquilla_ocupada = None
taquilla_libre = None
tarjeta_recibida = None

gc.collect()

# 🔄 Bucle Asíncrono Principal que maneja UART y Touch
async def main_async_loop():
    global state, num_introducido, locker_n, data, taquilla_ocupada, tarjeta_recibida

    while True:
        gc.collect()

        # 1. MANEJO DE UART (LECTOR DE TARJETAS)
        if uart.any():
            blink(verde,2,50)
            linea_bytes = uart.readline()

            if linea_bytes:
                tarjeta_recibida = linea_bytes.decode('utf-8').strip()
                if tarjeta_recibida:
                    print(f"Mensaje recibido (Tarjeta): {tarjeta_recibida}")
                    
                    # Recargar datos de persistencia
                    with open("persistencia", "r") as g:
                        data = json.load(g)

                    taquilla_asignada = None
                    taquilla_libre = None
                    
                    # Buscar si la tarjeta ya está asignada (Liberar)
                    for taquilla in data:
                        if tarjeta_recibida == taquilla['tarjeta']:
                            taquilla_asignada = taquilla
                            break
                    
                    # LÓGICA DE LIBERACIÓN (Tarjeta asignada)
                    if taquilla_asignada:
                        print(f"Tarjeta asignada a taquilla {taquilla_asignada['nombre']}. Iniciando liberación.")
                        
                        success = await send_command_via_ble(
                            taquilla_asignada['torre'],
                            'liberar',
                            taquilla_asignada['nombre']
                        )

                        if success:
                            blink(azul,2, 50)
                            # Actualizar persistencia: Liberar taquilla
                            taquilla_asignada['tarjeta'] = ''
                            with open("persistencia", "w") as g:
                                g.write(json.dumps(data))
                            
                            taquilla_ocupada = taquilla_asignada # Usado para la pantalla 'opening locker'
                            state = "opening locker"
                        else:
                            blink(rojo, 3, 100)
                            print("Error BLE al liberar.")


                    # LÓGICA DE ASIGNACIÓN (Tarjeta no asignada)
                    else:
                        print("Tarjeta sin taquilla asignada. Buscando libre.")
                        # Buscar taquilla libre
                        for taquilla in data:
                            if taquilla['tarjeta'] == '':
                                taquilla_libre = taquilla
                                break
                        
                        if taquilla_libre:
                            print(f"Taquilla libre encontrada: {taquilla_libre['nombre']}. Iniciando asignación.")
                            
                            success = await send_command_via_ble(
                                taquilla_libre['torre'],
                                'ocupar',
                                taquilla_libre['nombre']
                            )

                            if success:
                                blink(azul, 2, 50)
                                # Actualizar persistencia: Ocupar taquilla
                                taquilla_libre['tarjeta'] = tarjeta_recibida
                                with open("persistencia", "w") as g:
                                    g.write(json.dumps(data))

                                taquilla_ocupada = taquilla_libre # Usado para la pantalla 'opening locker'
                                state = "opening locker"
                            else:
                                blink(rojo, 3, 100)
                                print("Error BLE al ocupar.")

                        else:
                            print('No quedan taquillas disponibles.')
                            # (Podrías añadir una pantalla de error aquí)
                            blink(rojo, 3, 100) # Parpadeo de error

        # 2. MANEJO DE TOUCH Y ESTADOS DE PANTALLA (SIN MODIFICAR LÓGICA DE ESTADOS)
        # NOTA: En un bucle asíncrono, los time.sleep() deben ser await asyncio.sleep()
        
        # Lógica de Timeout (Mantener solo si es necesario, de lo contrario, el await sleep_ms(100) basta)
        if state in ("wait_for_PIN", "wait_for_locker_option", "choose_action"):
            # En asyncio, esto es más complejo, pero mantendremos la simplificación del sleep
            pass

        touch_coords = touch.raw_touch()
        if touch_coords:
            # inicio_timeout=time.ticks_ms() # No relevante en asyncio si no se usa el timeout
            pass

        ##### BLOQUE DE LÓGICA PARA INTERPRETAR LOS TOQUES EN LA PANTALLA #####
        if state == "start" and touch_coords:
            state="draw_keyboard"

        if state=="wait_for_PIN" and touch_coords:
            # ... (Lógica de PIN igual)
            tecla = detectar_valores(touch_coords)
            if tecla == 'DEL':
                # ... (Lógica de DEL)
                display.draw_text(x_center, y_center, num_introducido[-1] if num_introducido else ' ', font, black_color, black_color)
                num_introducido=num_introducido[:-1]
            elif tecla == 'ENT':
                display.draw_text(x_center, y_center, num_introducido, font, black_color, black_color)
                if num_introducido==password:
                    text_msg='PIN OK'
                    display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                    await asyncio.sleep_ms(500)
                    display.draw_text(x_center, y_center,text_msg, font, black_color, black_color)
                    num_introducido=''
                    state="draw_options"
                else:
                    text_msg='BAD PIN'
                    display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                    await asyncio.sleep_ms(500)
                    display.draw_text(x_center, y_center, text_msg, font, black_color, black_color)
                    num_introducido=''
            elif tecla: # Si es cualquier número
                num_introducido = num_introducido + tecla
            
            await asyncio.sleep_ms(300) # Sustitución del time.sleep(0.3)

        if state=="choose_action" and touch_coords:
            if touch_coords[1]<950:
                state="choose_locker"
            else:
                state="start"
                display.clear(hlines=5)
                pantalla_inicial()
                gc.collect()
        
        if state == "wait_for_locker_option" and touch_coords:
            # ... (Lógica de selección de taquilla igual)
            tecla = detectar_valores(touch_coords)
            if tecla == 'DEL':
                # ... (Lógica de DEL)
                locker_n=locker_n[:-1]
            elif tecla == 'ENT':
                # Lógica de CERRAR/LIBERAR taquilla introduciendo PIN
                with open("persistencia", "r") as g:
                    data = json.load(g)
                
                taquilla_a_cerrar = None
                for taquilla in data:
                    if taquilla['nombre'] == locker_n:
                        taquilla_a_cerrar = taquilla
                        break
                
                if taquilla_a_cerrar:
                    # SIMULACIÓN: Ya que el proceso real es por tarjeta, asumimos liberar.
                    # En un sistema real, se requeriría un PIN/Tarjeta para liberar.
                    print(f"Liberación manual de taquilla {locker_n} solicitada.")
                    
                    # Llamada a la función BLE
                    success = await send_command_via_ble(
                        taquilla_a_cerrar['torre'],
                        'liberar',
                        taquilla_a_cerrar['nombre']
                    )
                    
                    if success:
                        taquilla_a_cerrar['tarjeta']=''
                        with open("persistencia", "w") as g:
                            g.write(json.dumps(data))
                        
                        text_msg='LIBERANDO '+ locker_n
                        display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                        await asyncio.sleep_ms(500)
                        display.draw_text(x_center, y_center,text_msg, font, black_color, black_color)
                    else:
                        text_msg='ERR LIBERAR'
                        display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                        await asyncio.sleep_ms(500)
                        display.draw_text(x_center, y_center, text_msg, font, black_color, black_color)
                        
                    locker_n = ''

                else:
                    text_msg='NO EXISTE'
                    display.draw_text(x_center, y_center,text_msg, font, white_color, black_color)
                    await asyncio.sleep_ms(500)
                    display.draw_text(x_center, y_center, text_msg, font, black_color, black_color)
                    locker_n=''

            elif tecla: # Si es cualquier número
                locker_n = locker_n + tecla

            await asyncio.sleep_ms(300) # Sustitución del time.sleep(0.3)


        ##### BLOQUE DE LÓGICA PARA CONTROLAR QUÉ SE MUESTRA EN PANTALLA (Visualización) #####
        
        if state=="draw_keyboard":
            display.clear(hlines=5)
            formar_teclado()
            display.draw_text(x_center, y_center ,'PIN CODE', font, white_color, black_color)
            await asyncio.sleep_ms(1000) # Sustitución del time.sleep(1)
            display.draw_text(x_center, y_center ,'PIN CODE', font, black_color, black_color)
            state="wait_for_PIN"
            gc.collect()

        if state == "wait_for_PIN":
            display.draw_text(x_center, y_center ,num_introducido, font, white_color, black_color)

        if state == "wait_for_locker_option":
            display.draw_text(x_center, y_center ,locker_n, font, white_color, black_color)

        if state == "draw_options":
            display.clear(hlines=5 )
            pantalla_eleccion()
            state="choose_action"
            gc.collect()

        if state == "choose_locker":
            display.clear(hlines=5)
            formar_teclado()
            display.draw_text(0, 25 ,'CUAL ABRO', font, white_color, black_color)
            await asyncio.sleep_ms(500) # Sustitución del time.sleep(0.5)
            display.draw_text(0, 25 ,'CUAL ABRO', font, black_color, black_color)
            state="wait_for_locker_option"
            gc.collect()
            
        if state == "opening locker":
            gc.collect()
            display.clear(hlines=5)
            # Usamos taquilla_ocupada que fue guardado en el manejo de UART/BLE
            if taquilla_ocupada:
                taquilla_nombre = taquilla_ocupada['nombre']
                opening_locker_screen(taquilla=taquilla_nombre)
                await asyncio.sleep(3) # Sustitución del time.sleep(3)
                opening_locker_screen(borrar=True, taquilla=taquilla_nombre)
            
            # Resetear al estado inicial
            taquilla_ocupada = None
            state="start"
            pantalla_inicial()

        # Pausa para ceder el control al loop de asyncio
        await asyncio.sleep_ms(1)

# --- Ejecución Principal de la Tarea Asíncrona ---
try:
    asyncio.run(main_async_loop())
except Exception as e:
    print(f"Error fatal en el loop principal: {e}")
    try:
        sys.print_exception(e)
    except:
        machine.soft_reset()
        print('Error. Reiniciando')
