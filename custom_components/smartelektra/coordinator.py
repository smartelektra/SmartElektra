from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pymodbus.client import AsyncModbusTcpClient

from .const import CONF_COILS, CONF_HOST, CONF_PORT, CONF_SLAVE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmartElektraCoordinator(DataUpdateCoordinator[dict[int, bool]]):
    """Polls Modbus coils and keeps an in-memory state map: {coil_index: bool}."""

    def __init__(self, hass: HomeAssistant, entry_data: dict):
        self.hass = hass
        self.host: str = entry_data[CONF_HOST]
        self.port: int = int(entry_data[CONF_PORT])
        self.slave: int = int(entry_data[CONF_SLAVE])
        self.coils: int = int(entry_data[CONF_COILS])

        self._client = AsyncModbusTcpClient(self.host, port=self.port)
        self._lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.host}_{self.port}_s{self.slave}",
            update_interval=timedelta(seconds=1),
        )

    async def async_close(self) -> None:
        try:
            await self._client.close()
        except Exception:
            pass

    async def _ensure_connected(self) -> None:
        ok = await self._client.connect()
        if not ok:
            raise UpdateFailed(f"Cannot connect to Modbus TCP {self.host}:{self.port}")

    async def _async_update_data(self) -> dict[int, bool]:
        async with self._lock:
            await self._ensure_connected()
            rr = await self._client.read_coils(0, self.coils, slave=self.slave)
            if rr.isError():
                raise UpdateFailed(f"Modbus error reading coils (slave {self.slave})")
            bits = rr.bits[: self.coils]
            return {i: bool(bits[i]) for i in range(self.coils)}

    async def write_coil(self, coil: int, state: bool) -> None:
        async with self._lock:
            await self._ensure_connected()
            wr = await self._client.write_coil(coil, state, slave=self.slave)
            if wr.isError():
                raise UpdateFailed(f"Modbus error writing coil {coil} (slave {self.slave})")
