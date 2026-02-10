from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_COILS, CONF_DEVICE, CONF_HOST, CONF_PORT, CONF_SLAVE, DOMAIN
from .coordinator import SmartElektraCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = SmartElektraCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    coils = int(entry.data[CONF_COILS])
    entities = [SmartElektraRelaySwitch(coordinator, entry, coil=i) for i in range(coils)]
    async_add_entities(entities)


class SmartElektraRelaySwitch(CoordinatorEntity[SmartElektraCoordinator], SwitchEntity):
    _attr_icon = "mdi:relay"

    def __init__(self, coordinator: SmartElektraCoordinator, entry: ConfigEntry, coil: int):
        super().__init__(coordinator)
        self._entry = entry
        self._coil = coil

        host = entry.data[CONF_HOST]
        port = entry.data[CONF_PORT]
        slave = entry.data[CONF_SLAVE]

        self._attr_name = f"Przekaźnik {coil + 1}"
        self._attr_unique_id = f"{DOMAIN}_{host}_{port}_s{slave}_c{coil}"

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._coil) if self.coordinator.data else None

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.write_coil(self._coil, True)
        self.coordinator.data[self._coil] = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.write_coil(self._coil, False)
        self.coordinator.data[self._coil] = False
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        host = self._entry.data[CONF_HOST]
        port = self._entry.data[CONF_PORT]
        slave = self._entry.data[CONF_SLAVE]
        device = self._entry.data.get(CONF_DEVICE, "mini")

        return DeviceInfo(
            identifiers={(DOMAIN, f"{host}:{port}:slave{slave}")},
            name=f"SmartElektra Slave {slave}",
            manufacturer="SmartElektra",
            model=f"{device.upper()} (Modbus RTU via TCP gateway)",
        )
