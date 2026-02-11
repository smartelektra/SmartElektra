from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, RELAYS_COUNT
from .coordinator import RelayDataCoordinator


@dataclass(frozen=True)
class RelayDescription:
    index: int
    name: str


RELAY_DESCRIPTIONS = [
    RelayDescription(0, "Przekaźnik 1"),
    RelayDescription(1, "Przekaźnik 2"),
    RelayDescription(2, "Przekaźnik 3"),
    RelayDescription(3, "Przekaźnik 4"),
    RelayDescription(4, "Przekaźnik 5"),
    RelayDescription(5, "Przekaźnik 6"),
    RelayDescription(6, "Przekaźnik 7"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RelayDataCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([ArduinoRelaySwitch(entry, coordinator, client, d) for d in RELAY_DESCRIPTIONS])


class ArduinoRelaySwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, entry, coordinator: RelayDataCoordinator, client, desc: RelayDescription) -> None:
        self._entry = entry
        self._coordinator = coordinator
        self._client = client
        self._desc = desc

        self._attr_unique_id = f"{entry.entry_id}_relay_{desc.index}"
        self._attr_name = desc.name

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    @property
    def is_on(self) -> bool | None:
        data = self._coordinator.data
        if not data or len(data) < RELAYS_COUNT:
            return None
        return bool(data[self._desc.index])

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._coordinator.async_add_listener(self.async_write_ha_state))
        await self._coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs) -> None:
        addr = self._coordinator.base_address + self._desc.index
        await self._client.write_coil(addr, True, self._coordinator.slave)
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        addr = self._coordinator.base_address + self._desc.index
        await self._client.write_coil(addr, False, self._coordinator.slave)
        await self._coordinator.async_request_refresh()
