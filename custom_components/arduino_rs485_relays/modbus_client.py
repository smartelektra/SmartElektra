from __future__ import annotations

import threading
from typing import List

from pymodbus.client import ModbusTcpClient


class ModbusTcpCoilClient:
    """Conservative Modbus TCP client (sync).

    All methods are blocking; call them from HA executor threads.
    """

    def __init__(self, host: str, port: int, timeout: float = 5.0) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._client = ModbusTcpClient(host=host, port=port, timeout=timeout)
        self._lock = threading.Lock()

    def close(self) -> None:
        with self._lock:
            try:
                self._client.close()
            except Exception:
                pass

    def _ensure_connected(self) -> None:
        if not self._client.connect():
            raise ConnectionError(f"Cannot connect to {self._host}:{self._port}")

    def read_coils(self, address: int, count: int, slave_id: int) -> List[bool]:
        with self._lock:
            self._ensure_connected()
            rr = self._client.read_coils(address, count=count, slave=slave_id)
            if rr is None:
                self._client.close()
                raise ConnectionError("No response (None) from read_coils")
            if rr.isError():
                raise RuntimeError(f"Modbus read_coils error: {rr}")
            return list(rr.bits[:count])

    def write_coil(self, address: int, value: bool, slave_id: int) -> None:
        with self._lock:
            self._ensure_connected()
            rr = self._client.write_coil(address, value, slave=slave_id)
            if rr is None:
                self._client.close()
                raise ConnectionError("No response (None) from write_coil")
            if rr.isError():
                raise RuntimeError(f"Modbus write_coil error: {rr}")
