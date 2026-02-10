from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import SmartElektraCoordinator
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_SLAVE, CONF_DEVICE, CONF_COILS

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = SmartElektraCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    coils = entry.data[CONF_COILS]
    async_add_entities(
        SmartElektraSwitch(coordinator, entry, i)
        for i in range(coils)
    )

class SmartElektraSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, entry, coil):
        super().__init__(coordinator)
        self._entry = entry
        self._coil = coil
        self._attr_name = f"Przekaźnik {coil+1}"
        self._attr_unique_id = f"{DOMAIN}_{entry.data[CONF_HOST]}_{entry.data[CONF_SLAVE]}_{coil}"
        self._attr_icon = "mdi:relay"

    @property
    def is_on(self):
        if self.coordinator.data:
            return self.coordinator.data[self._coil]
        return False

    async def async_turn_on(self, **kwargs):
        await self.coordinator.write_coil(self._coil, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.write_coil(self._coil, False)
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._entry.data[CONF_HOST]}:{self._entry.data[CONF_SLAVE]}")},
            name=f"SmartElektra Slave {self._entry.data[CONF_SLAVE]}",
            manufacturer="SmartElektra",
            model=self._entry.data[CONF_DEVICE].upper(),
        )
