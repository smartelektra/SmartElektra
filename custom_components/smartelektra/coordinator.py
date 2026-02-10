from pymodbus.client import AsyncModbusTcpClient
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from datetime import timedelta

from .const import CONF_HOST, CONF_PORT, CONF_SLAVE, CONF_COILS

class SmartElektraCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, data):
        self.host = data[CONF_HOST]
        self.port = data[CONF_PORT]
        self.slave = data[CONF_SLAVE]
        self.coils = data[CONF_COILS]
        self.client = AsyncModbusTcpClient(self.host, port=self.port)

        super().__init__(
            hass,
            logger=None,
            name="SmartElektra",
            update_interval=timedelta(seconds=5),
        )

    async def _async_update_data(self):
        await self.client.connect()
        result = await self.client.read_coils(0, self.coils, slave=self.slave)
        return result.bits if result else {}

    async def write_coil(self, coil, value):
        await self.client.write_coil(coil, value, slave=self.slave)
