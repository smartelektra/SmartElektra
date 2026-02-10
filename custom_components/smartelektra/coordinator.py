from __future__ import annotations

import asyncio
import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_COILS, CONF_HOST, CONF_PORT, CONF_SLAVE, DOMAIN

_LOGGER = logging.getLogger(__name__)

from pymodbus.client import ModbusTcpClient  # type: ignore


def _merged(entry: ConfigEntry) -> dict:
    data = dict(entry.data)
    data.update(entry.options)
    return data


class SmartElektraCoordinator(DataUpdateCoordinator[dict[int, bool]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        cfg = _merged(entry)
        self.host: str = cfg[CONF_HOST]
        self.port: int = int(cfg[CONF_PORT])
        self.slave: int = int(cfg[CONF_SLAVE])
        self.coils: int = int(cfg[CONF_COILS])

        self._client: ModbusTcpClient | None = None
        self._lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({self.host}:{self.port} slave {self.slave})",
            update_interval=datetime.timedelta(seconds=1),
        )

    async def async_close(self) -> None:
        if self._client is None:
            return
        await self.hass.async_add_executor_job(self._client.close)
        self._client = None

    def _get_client(self) -> ModbusTcpClient:
        if self._client is None:
            self._client = ModbusTcpClient(host=self.host, port=self.port, timeout=2)
        return self._client

    async def _async_read_coils(self) -> dict[int, bool]:
        def _read() -> dict[int, bool]:
            client = self._get_client()
            if not client.connect():
                raise OSError("Modbus TCP connect failed")
            rr = client.read_coils(0, self.coils, unit=self.slave)
            if rr.isError():  # type: ignore[no-untyped-call]
                raise OSError(f"Modbus read_coils error: {rr}")
            bits = list(getattr(rr, "bits", []))[: self.coils]
            return {i: bool(bits[i]) for i in range(len(bits))}

        async with self._lock:
            return await self.hass.async_add_executor_job(_read)

    async def _async_write_coil(self, address: int, state: bool) -> None:
        def _write() -> None:
            client = self._get_client()
            if not client.connect():
                raise OSError("Modbus TCP connect failed")
            rr = client.write_coil(address, state, unit=self.slave)
            if rr.isError():  # type: ignore[no-untyped-call]
                raise OSError(f"Modbus write_coil error: {rr}")

        async with self._lock:
            await self.hass.async_add_executor_job(_write)

    async def write_coil(self, address: int, state: bool) -> None:
        await self._async_write_coil(address, state)
        try:
            await self.async_request_refresh()
        except Exception:  # noqa: BLE001
            pass

    async def _async_update_data(self) -> dict[int, bool]:
        try:
            return await self._async_read_coils()
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err
