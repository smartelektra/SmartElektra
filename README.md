# SmartElektra

Integracja Home Assistant do sterowania 7 przekaźnikami (coils) przez Modbus TCP (bramka RS485→ETH) dla Twojego Arduino.

## Funkcje
- Konfiguracja w UI: IP, port, slave, adres bazowy, interwał odczytu
- 7 encji typu `switch` (Przekaźnik 1..7)
- Synchronizacja stanu (przycisk fizyczny na Arduino → stan w HA przez polling)

## Instalacja (manual)
Skopiuj folder `custom_components/smartelektra` do `/config/custom_components/` i zrestartuj HA.

## Uwaga
Zmiana domeny z `arduino_rs485_relays` na `smartelektra` oznacza, że stara integracja/encje nie migrują automatycznie.
Usuń starą integrację i dodaj SmartElektra od nowa.
