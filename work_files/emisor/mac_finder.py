import network
import time
 
# Create a WLAN station interface
wlan = network.WLAN(network.STA_IF)

# Activate the interface
wlan.active(True)

# Wait a moment for the interface to initialize
time.sleep(0.5)

# Get the MAC address
mac_bytes = wlan.config('mac')
print(mac_bytes)
# Convierte los bytes a una cadena hexadecimal y luego formatea con dos puntos.
mac_address = ':'.join(f'{byte:02x}' for byte in mac_bytes)
print(f"Dirección MAC formateada: {mac_address}")


