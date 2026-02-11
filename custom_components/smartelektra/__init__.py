from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_COILS, CONF_DEVICE, DOMAIN
from .coordinator import SmartElektraCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["switch"]


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options updates."""
    coordinator: SmartElektraCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.entry = entry  # keep reference fresh

    # If device/coils changed, reload entry to recreate entities.
    merged = {**entry.data, **entry.options}
    new_coils = int(merged.get(CONF_COILS, coordinator.coils))
    new_device = merged.get(CONF_DEVICE)

    if new_coils != coordinator.coils or (new_device and new_device != merged.get(CONF_DEVICE)):
        _LOGGER.info("Config changed (coils/device). Reloading entry %s", entry.entry_id)
        await hass.config_entries.async_reload(entry.entry_id)
        return

    # Otherwise just push config to Arduino and refresh.
    try:
        await coordinator.apply_options_to_device()
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Failed to apply options to device: %s", err)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = SmartElektraCoordinator(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # Do not block HA startup if the gateway is temporarily unreachable.
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("First refresh failed (%s). Entities will be unavailable until connection works.", err)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Try to push current options to Arduino (best-effort).
    try:
        await coordinator.apply_options_to_device()
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Skipping apply_options_to_device on setup: %s", err)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: SmartElektraCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()
    return unload_ok
