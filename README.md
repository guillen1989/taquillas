# Smart Locker System with ESP32 and Bluetooth Low Energy (BLE)

## Functionality
Locker opening achieved through a **touch interface** and **BLE wireless communication** with a relay module. Card reading is performed by an **RFID module** which transmits information via UART.

## Hardware Used (Bill Of Materials - BOM)

* **Locker Tower Control:** ESP32-C3 Mini.
* **Master Module / Touch Display:** TFT LCD 3.2"/3.5" (ILI9341 with XPT2046 controller), also known as the **Cheap Yellow Display**.
* **Voltage Regulator:** LM2596S Module (Single Power Supply Unit).
* **Actuators:** Relay Modules (4 channels).
* **Loads:** Electromagnetic Locks (Solenoid Locks).
* **Critical Protection:** **1N4007 Flyback Diodes** (installed in parallel with each electromagnetic lock).
    * *The diodes are essential to prevent the ESP32 controlling the locks from rebooting, a problem caused by the **inductive kickback noise** generated when the solenoids open.*

## Connections and Diagrams

* **Block Diagram showing Data Flow**
    ![Block Diagram](hardware/Block_diagram.png)
    [PDF with the Block Diagram](hardware/PDF_Block_diagram.pdf)

* **Detailed Schematic**
    
    * **GPIOs used for relays:** 3, 7, 9, 20.
    
    * **GPIOs for RFID Reader:** TO BE COMPLETED
    
    * **SPI Pins for the Display:** May vary depending on the Cheap Yellow Display manufacturer.
    
    * **UART Pins**
        * **Display:**
            1.  Transmitter (TX): pin 22
            2.  Receiver (RX): pin 20
        * **RFID Reader:**
            1.  Transmitter (TX): pin 10
            2.  Receiver (RX): pin 1
    
    * **KEY Maintenance Note:** If the system presents failures or reboots (**WDT Timeout**), the problem is **noise**. Verify that the **1N4007 diodes** remain correctly soldered on the locks. If a different power supply is used, consider an **L-C filter** or a **dual power supply** configuration.

    ![Schematic diagram of the central module and the RFID reader](hardware/Screen_RFID_reader_diagram.png)
    ![Schematic diagram of the locker tower](hardware/Locker_tower_diagram.png)
    [PDF with these schematic diagrams](hardware/Schematic_diagrams.pdf)

## Software Architecture (Firmware)

* [display.py](firmware/display.pi) (**Master Control Module**): Main logic, touch interface, and **BLE Master** to send opening commands.
* [1tower.py](firmware/1torre.py), [2tower.py](firmware/2torre.py), 3tower.py... (**Relay Modules**): **BLE Slave** that receives commands and controls the state of the **relay pins** (Pin 3, 7, 9, 20).
* [RFID\_reader.py](firmware/RFID_reader.py) (**RFID Reader**): RFID reading logic (MFRC522) and communication via **UART** with the control module.

## Setup and Installation (For Future Maintainers)

**Dependencies** require **MicroPython** and the following libraries: `aioble`, `micropython-ili9341`, `mfrc522`.

**Flashing Process**

Instructions to install MicroPython firmware on the Cheap Yellow Display (`firmware/flash_files/esp32.bin`) and on the ESP32 C3 Super Mini boards (`firmware/flash_files/c3generic.bin`).

To execute the code on the ESP32 boards that control the entire system, firmware that runs MicroPython must first be installed on each board. Use the provided files: `firmware/flash_files/esp32.bin` for the Cheap Yellow Display and `firmware/flash_files/c3generic.bin` for the ESP32 C3 Super Mini boards. There are several ways to do this:

[Using the Thonny program, with a graphical interface](https://docs.sunfounder.com/projects/esp32-starter-kit/es/latest/micropython/python_start/install_micropython.html)

[Using esptool in the command line](https://randomnerdtutorials.com/flashing-micropython-firmware-esptool-py-esp32-esp8266/)
