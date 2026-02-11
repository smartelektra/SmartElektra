from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_PORT, DOMAIN, PLATFORMS
from .coordinator import RelayDataCoordinator
from .modbus_client import ModbusTcpCoilClient


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    client = ModbusTcpCoilClient(entry.data[CONF_HOST], entry.data[CONF_PORT], timeout=5.0)
    coordinator = RelayDataCoordinator(hass, client, entry)

    hass.data[DOMAIN][entry.entry_id] = {"client": client, "coordinator": coordinator}

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id, None)
        if data:
            await data["client"].async_close()
    return unload_ok
