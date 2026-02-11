from __future__ import annotations

import asyncio
import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pymodbus.client import ModbusTcpClient  # type: ignore

from .const import (
    CFG_BTN_MONO,
    CFG_HA_MONO,
    CFG_INVERT,
    CONF_COILS,
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE,
    DOMAIN,
    HREG_CFG_BASE,
    HREG_COMMIT,
    HREG_PULSE_BASE,
)

_LOGGER = logging.getLogger(__name__)


def _merged(entry: ConfigEntry) -> dict:
    data = dict(entry.data)
    data.update(entry.options)
    return data


def _opt_key(prefix: str, i: int) -> str:
    return f"{prefix}_{i+1}"


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

    def reload_from_entry(self) -> None:
        """Re-read host/port/slave/coils from current entry data/options."""
        cfg = _merged(self.entry)
        self.host = cfg[CONF_HOST]
        self.port = int(cfg[CONF_PORT])
        self.slave = int(cfg[CONF_SLAVE])
        self.coils = int(cfg[CONF_COILS])

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

    async def _async_write_register(self, address: int, value: int) -> None:
        def _write() -> None:
            client = self._get_client()
            if not client.connect():
                raise OSError("Modbus TCP connect failed")
            rr = client.write_register(address, value, unit=self.slave)
            if rr.isError():  # type: ignore[no-untyped-call]
                raise OSError(f"Modbus write_register error: {rr}")

        async with self._lock:
            await self.hass.async_add_executor_job(_write)

    async def _async_write_registers(self, address: int, values: list[int]) -> None:
        def _write() -> None:
            client = self._get_client()
            if not client.connect():
                raise OSError("Modbus TCP connect failed")
            rr = client.write_registers(address, values, unit=self.slave)
            if rr.isError():  # type: ignore[no-untyped-call]
                raise OSError(f"Modbus write_registers error: {rr}")

        async with self._lock:
            await self.hass.async_add_executor_job(_write)

    async def write_coil(self, address: int, state: bool) -> None:
        await self._async_write_coil(address, state)
        try:
            await self.async_request_refresh()
        except Exception:  # noqa: BLE001
            pass

    async def apply_options_to_device(self) -> None:
        """Push per-channel configuration (invert/mono/pulse) to Arduino via holding registers and commit."""
        self.reload_from_entry()
        opts = self.entry.options or {}
        coils = int(self.coils)

        pulse_default = int(opts.get("pulse_default_ms", 300))

        flags: list[int] = []
        pulses: list[int] = []

        for i in range(coils):
            inv = bool(opts.get(_opt_key("invert", i), False))
            btn_mono = bool(opts.get(_opt_key("btn_mono", i), False))
            ha_mono = bool(opts.get(_opt_key("ha_mono", i), False))
            pulse_ms = int(opts.get(_opt_key("pulse_ms", i), pulse_default))

            f = 0
            if inv:
                f |= CFG_INVERT
            if btn_mono:
                f |= CFG_BTN_MONO
            if ha_mono:
                f |= CFG_HA_MONO

            flags.append(int(f))
            pulse_ms = max(50, min(5000, int(pulse_ms)))
            pulses.append(pulse_ms)

        # Write flags (HREG 0..)
        await self._async_write_registers(HREG_CFG_BASE, flags)
        # Write pulse times (HREG 100..)
        await self._async_write_registers(HREG_PULSE_BASE, pulses)
        # Commit to EEPROM on Arduino
        await self._async_write_register(HREG_COMMIT, 1)

        # Refresh states (optional)
        try:
            await self.async_request_refresh()
        except Exception:  # noqa: BLE001
            pass

    async def _async_update_data(self) -> dict[int, bool]:
        try:
            self.reload_from_entry()
            return await self._async_read_coils()
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err
