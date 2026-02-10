# SmartElektra (Home Assistant custom integration)

Integracja tworzy przełączniki przekaźników po Modbus TCP (brama RS485→ETH) dla Arduino jako Modbus RTU slave.

## Kreator (Config Flow)
Wybierasz:
- IP bramy (Modbus TCP)
- port (domyślnie 502)
- slave (ID Arduino po RS485)
- typ: **mini** (UNO = 7 przekaźników) lub **mega** (MEGA = 30 przekaźników)

Przełączniki dodają się automatycznie (7 albo 30).

## Instalacja przez HACS (Custom repository)
1. Wgraj to repo na GitHub.
2. HACS → Integrations → ⋮ → Custom repositories → dodaj URL repo (Type: Integration).
3. Zainstaluj SmartElektra w HACS i zrestartuj HA.

## Ważne
Uzupełnij w `manifest.json` swoje:
- documentation
- issue_tracker
- codeowners
