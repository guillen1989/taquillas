
# Control de Taquillas Inteligentes con ESP32-C3 y BLE
# Funcionalidad
Apertura de taquillas mediante interfaz táctil y comunicación inalámbrica BLE con un módulo de relés, y un módulo RFID vía UART
# Hardware Utilizado (Bill Of Materials)
* Control de cada torre de taquillas: ESP32-C3 Mini.
* Módulo maestro/pantalla táctil: TFT LCD de 3.2"/3.5" (ILI9341 con controlador XPT2046).
* Regulador de Voltaje: Módulo LM2596S (Fuente de alimentación única).
* Actuadores: Módulos de Relé (4 canales).
* Cargas: Cerraduras Electromagnéticas (Electroimanes).
* Protección Crítica: Diodos de Volante 1N4007 (instalados en paralelo con cada cerradura electromagnética). 
*Los diodos son imprescindibles para evitar el reinicio del esp32 que controla las cerraduras causado por el ruido inductivo que se produce al abrirse el solenoide de las cerraduras.*
# Conexiones y Diagramas
* Diagrama de Bloques: Incluye una imagen (diagrama_bloques.png) para mostrar el flujo de datos (Taquilla Central $\leftrightarrow$ Módulo Control BLE; Módulo RFID $\rightarrow$ Módulo Control UART).
![Diagrama de bloques](https://github.com/guillen1989/taquillas/hardware/Block diagram.png)
* Esquemático Detallado: Enlaza al archivo esquematico.pdf y describe brevemente dónde se conectan los pines críticos (GPIOs usados para los relés, pines SPI para la pantalla, pines UART).Aislamiento de Ruido (Nota de Mantenimiento CLAVE): Si el sistema presenta fallos o reinicios (WDT Timeout), el problema es ruido. Verifique que los Diodos 1N4007 sigan correctamente soldados en las cerraduras. Si se usa una fuente de alimentación diferente, considerar un filtro L-C o una doble fuente de alimentación.
# Arquitectura de Software (Firmware)
* display.py (Módulo de control): Lógica principal, interfaz táctil, y Master BLE para enviar comandos de apertura.
* 1torre.py, 2torre.py, 3torre.py.. (Módulo Relés): Slave BLE que recibe comandos y controla el estado de los pines de relé (Pin 3, 7, 9, 20).
* RFID_reader.py (Lector RFID): Lógica de lectura RFID (MFRC522) y comunicación por UART con el módulo de control.
# Configuración e Instalación (Para Futuros Mantenedores)
* Dependencias: requiere MicroPython y las siguientes librerías: aioble, micropython-ili9341, mfrc522.
* Proceso de Flasheo: Pasos necesarios para cargar el firmware en los ESP32.
* IDs Críticos: Lista los UUIDs del servicio y las características BLE para facilitar el debugging de la comunicación inalámbrica.
