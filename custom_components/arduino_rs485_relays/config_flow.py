from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_BASE_ADDRESS,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DEFAULT_BASE_ADDRESS,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    DOMAIN,
)
from .modbus_client import ModbusTcpCoilClient


STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SLAVE, default=DEFAULT_SLAVE): int,
        vol.Optional(CONF_BASE_ADDRESS, default=DEFAULT_BASE_ADDRESS): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            client = ModbusTcpCoilClient(user_input[CONF_HOST], user_input[CONF_PORT], timeout=5.0)
            try:
                await client.read_coils(
                    address=user_input[CONF_BASE_ADDRESS],
                    count=1,
                    slave_id=user_input[CONF_SLAVE],
                )
            except Exception:
                errors["base"] = "cannot_connect"
            finally:
                await client.async_close()

            if not errors:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_SLAVE]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Arduino RS485 Relays", data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self._entry.data
        opts = self._entry.options

        schema = vol.Schema(
            {
                vol.Optional(CONF_SLAVE, default=opts.get(CONF_SLAVE, data[CONF_SLAVE])): int,
                vol.Optional(CONF_BASE_ADDRESS, default=opts.get(CONF_BASE_ADDRESS, data[CONF_BASE_ADDRESS])): int,
                vol.Optional(CONF_SCAN_INTERVAL, default=opts.get(CONF_SCAN_INTERVAL, data[CONF_SCAN_INTERVAL])): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
