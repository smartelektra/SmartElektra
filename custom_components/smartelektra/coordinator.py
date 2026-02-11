from __future__ import annotations

import logging
from datetime import timedelta
from typing import List

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_BASE_ADDRESS, CONF_SCAN_INTERVAL, CONF_SLAVE, RELAYS_COUNT
from .modbus_client import ModbusTcpCoilClient

_LOGGER = logging.getLogger(__name__)


class RelayDataCoordinator(DataUpdateCoordinator[List[bool]]):
    def __init__(self, hass: HomeAssistant, client: ModbusTcpCoilClient, entry) -> None:
        self._client = client
        self._entry = entry
        scan = entry.options.get(CONF_SCAN_INTERVAL, entry.data[CONF_SCAN_INTERVAL])
        super().__init__(
            hass,
            _LOGGER,
            name="SmartElektra",
            update_interval=timedelta(seconds=scan),
        )

    @property
    def slave(self) -> int:
        return self._entry.options.get(CONF_SLAVE, self._entry.data[CONF_SLAVE])

    @property
    def base_address(self) -> int:
        return self._entry.options.get(CONF_BASE_ADDRESS, self._entry.data[CONF_BASE_ADDRESS])

    async def _async_update_data(self) -> List[bool]:
        try:
            return await self.hass.async_add_executor_job(
                self._client.read_coils,
                self.base_address,
                RELAYS_COUNT,
                self.slave,
            )
        except Exception as err:
            raise UpdateFailed(str(err)) from err
