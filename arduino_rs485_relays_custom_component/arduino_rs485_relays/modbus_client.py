from __future__ import annotations

import asyncio
import inspect
from typing import List

from pymodbus.client import AsyncModbusTcpClient


class ModbusTcpCoilClient:
    """Minimal client for Modbus TCP coils: read 7 coils + write single coil."""

    def __init__(self, host: str, port: int, timeout: float = 5.0) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._client: AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

    async def async_connect(self) -> None:
        if self._client is None:
            self._client = AsyncModbusTcpClient(
                host=self._host,
                port=self._port,
                timeout=self._timeout,
            )
        await self._client.connect()

    async def async_close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _unit_kwarg(self, func, slave_id: int) -> dict:
        """Handle pymodbus argument name differences (slave/device_id/unit)."""
        sig = inspect.signature(func)
        if "slave" in sig.parameters:
            return {"slave": slave_id}
        if "device_id" in sig.parameters:
            return {"device_id": slave_id}
        if "unit" in sig.parameters:
            return {"unit": slave_id}
        return {}

    async def read_coils(self, address: int, count: int, slave_id: int) -> List[bool]:
        async with self._lock:
            await self.async_connect()
            assert self._client is not None
            kw = self._unit_kwarg(self._client.read_coils, slave_id)
            rr = await self._client.read_coils(address, count=count, **kw)
            if rr.isError():
                raise RuntimeError(f"Modbus read_coils error: {rr}")
            return list(rr.bits[:count])

    async def write_coil(self, address: int, value: bool, slave_id: int) -> None:
        async with self._lock:
            await self.async_connect()
            assert self._client is not None
            kw = self._unit_kwarg(self._client.write_coil, slave_id)

            # write_coil usually accepts bool; some stacks accept list-of-bools.
            rr = await self._client.write_coil(address, value, **kw)
            if rr.isError():
                # fallback: list
                rr2 = await self._client.write_coil(address, [value], **kw)
                if rr2.isError():
                    raise RuntimeError(f"Modbus write_coil error: {rr2}")
