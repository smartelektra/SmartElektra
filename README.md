# SmartElektra (Home Assistant)

Integracja dodaje przełączniki przekaźników po Modbus RTU przez bramę **RS485→ETH (Modbus TCP)**.

## Instalacja przez HACS (Custom repository)
1. HACS → **Integrations** → menu (⋮) → **Custom repositories**
2. URL: `https://github.com/smartelektra/SmartElektra` (lub Twoje repo)  
   Category: **Integration**
3. Zainstaluj → **Restart Home Assistant**

## Ręcznie
Skopiuj folder:
`custom_components/smartelektra/`
do katalogu konfiguracji HA, potem restart.

## Konfiguracja
Ustawienia → Integracje → **Dodaj integrację** → SmartElektra  
W kreatorze wybierasz:
- host (IP bramy)
- port (domyślnie 502)
- slave
- typ: **mini (7 przekaźników)** / **mega (30 przekaźników)**

Encje pojawią się jako `Przekaźnik 1..N` w urządzeniu SmartElektra.

## Uwagi
- Integracja nie pobiera zależności z internetu (brak `requirements`), żeby działała na instalacjach offline.
- Jeśli brama nie odpowiada, encje będą **niedostępne** do czasu aż połączenie wróci.
