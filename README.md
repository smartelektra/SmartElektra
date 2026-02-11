# Arduino RS485 Relays (Modbus TCP)

Custom Home Assistant integration for Arduino UNO + RS485 + Modbus TCP gateway.

## Features

- UI configuration (IP, Port, Slave, Base address, Scan interval)
- 7 relays (coil 0–6)
- Real-time state sync (physical button updates HA)
- Works with Modbus TCP (RS485→ETH gateway)

## Requirements

- Arduino with Modbus RTU firmware
- RS485 to Ethernet gateway in Modbus TCP mode
- Home Assistant 2024+

## Installation

Copy the `custom_components/arduino_rs485_relays` folder
into your Home Assistant `/config/custom_components/` directory.

Restart Home Assistant.

Add integration:  
Settings → Devices & Services → Add Integration → Arduino RS485 Relays