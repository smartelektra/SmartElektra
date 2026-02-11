# Arduino RS485 Relays (Modbus TCP)

Custom Home Assistant integration for Arduino UNO + RS485 + Modbus TCP gateway.

## Features
- UI configuration (IP, Port, Slave, Base address, Scan interval)
- 7 relays mapped to coils base..base+6 (default base=0)
- State sync: physical button changes are reflected in HA (polling)

## Installation (manual)
Copy `custom_components/arduino_rs485_relays` into your HA `/config/custom_components/` and restart HA.

## Installation (HACS)
Add this repository as a custom repository (type: Integration), install, restart HA.
