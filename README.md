
# Control de Taquillas Inteligentes con ESP32 y Bluetooth de Baja Energía (BLE)
# Funcionalidad
Apertura de taquillas mediante interfaz táctil y comunicación inalámbrica BLE con un módulo de relés, y un módulo RFID vía UART
# Hardware Utilizado (Bill Of Materials)
* Control de cada torre de taquillas: ESP32-C3 Mini.
* Módulo maestro/pantalla táctil: TFT LCD de 3.2"/3.5" (ILI9341 con controlador XPT2046) También conocido como Cheap Yellow Display.
* Regulador de Voltaje: Módulo LM2596S (Fuente de alimentación única).
* Actuadores: Módulos de Relé (4 canales).
* Cargas: Cerraduras Electromagnéticas (Electroimanes).
* Protección Crítica: Diodos de Volante 1N4007 (instalados en paralelo con cada cerradura electromagnética). 
*Los diodos son imprescindibles para evitar el reinicio del esp32 que controla las cerraduras causado por el ruido inductivo que se produce al abrirse el solenoide de las cerraduras.*
# Conexiones y Diagramas
* Diagrama de bloques mostrando el flujo de datos
  ![Diagrama de bloques](hardware/Block_diagram.png)
  [PDF con el diagrama de bloques](hardware/PDF_Block_diagram.pdf)

* Esquemático Detallado
  
  **GPIOs usados para los relés:**  3, 7, 9, 20.
  
  **GPIOs para el lector RFID:** COMPLETAR
  
  **Pines SPI para la pantalla:** Pueden variar según el fabricante del Cheap Yellow Display.
  
  **Pines UART**
  
  * Pantalla
  1. Emisor: pin 22
  2. Receptor: pin 20
  * Lector RFID
  1. Emisor: pin 10
  2. Receptor: pin 1
     
  Nota de Mantenimiento CLAVE: Si el sistema presenta fallos o reinicios (WDT Timeout), el problema es ruido. Verifique que los Diodos 1N4007 sigan correctamente soldados en las cerraduras. Si se usa una fuente de alimentación diferente, considerar un filtro L-C o una doble fuente de alimentación.
  
  ![Diagrama esquemático de la torre de taquillas](hardware/Locker_tower_diagram.png)
  ![Diagrama esquemático del módulo central y el lector RFID](hardware/Screen_RFID_reader_diagram.png)
   [PDF con estos mismos diagramas esquemáticos](hardware/Schematic_diagrams.pdf)
# Arquitectura de Software (Firmware)
* display.py (Módulo de control): Lógica principal, interfaz táctil, y Master BLE para enviar comandos de apertura.
* 1torre.py, 2torre.py, 3torre.py.. (Módulo Relés): Slave BLE que recibe comandos y controla el estado de los pines de relé (Pin 3, 7, 9, 20).
* RFID_reader.py (Lector RFID): Lógica de lectura RFID (MFRC522) y comunicación por UART con el módulo de control.
# Configuración e Instalación (Para Futuros Mantenedores)

**Dependencias** requiere MicroPython y las siguientes librerías: aioble, micropython-ili9341, mfrc522.

**Proceso de Flasheo** 

Instrucciones para instalar micropython en el Cheap Yellow Display (firmware/flash_files/esp32.bin ) y en las placas ESP32 C3 super mini (firmware/flash_files/c3generic.bin)

Para poder ejecutar el código en las placas ESP32 que controlan todo el sistema, primero hay que instalar en cada placa un firmware que ejecute micropython. Para el Cheap Yellow Display (firmware/flash_files/esp32.bin ) y para las placas ESP32 C3 super mini (firmware/flash_files/c3generic.bin). Hay varias formas de hacerlo:

[Usando el programa Thonny, con interfaz gráfica](https://docs.sunfounder.com/projects/esp32-starter-kit/es/latest/micropython/python_start/install_micropython.html)

[Mediante esptool en la línea de comandos](https://randomnerdtutorials.com/flashing-micropython-firmware-esptool-py-esp32-esp8266/)

**IDs Críticos**

Lista los UUIDs del servicio y las características BLE para facilitar el debugging de la comunicación inalámbrica.
