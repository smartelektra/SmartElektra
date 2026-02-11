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


## Opcje kanałów (Arduino jako „mózg”)
Jeżeli masz wgrany firmware Arduino z obsługą konfiguracji przez rejestry (invert/mono/pulse + EEPROM commit),
to w integracji pojawi się **Konfiguruj** (Options) z polami:

- `invert_X` – odwróć logikę wyjścia dla kanału X (HIGH/LOW)
- `btn_mono_X` – przycisk lokalny monostabilny (impuls) dla kanału X
- `ha_mono_X` – sterowanie z HA jako impuls (ON = impuls, auto-OFF) dla kanału X
- `pulse_ms_X` – czas impulsu w ms (50–5000)
- `pulse_default_ms` – domyślny czas impulsu (ułatwia ustawianie wielu kanałów)

Po zapisie opcji integracja zapisuje:
- HREG `0..N-1` (cfg_flags),
- HREG `100..100+N-1` (pulse_ms),
- HREG `200` = commit (zapis do EEPROM w Arduino).

Jeżeli firmware Arduino nie obsługuje holding registers – przełączniki nadal będą działać, ale opcje nie zapiszą się do urządzenia.

