from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    COILS_BY_DEVICE,
    CONF_COILS,
    CONF_DEVICE,
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE,
    DEFAULT_PORT,
    DEFAULT_SLAVE,
    DEVICE_MEGA,
    DEVICE_MINI,
    DOMAIN,
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            device = user_input[CONF_DEVICE]
            user_input[CONF_COILS] = COILS_BY_DEVICE[device]

            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:s{user_input[CONF_SLAVE]}"
            )
            self._abort_if_unique_id_configured()

            title = f"SmartElektra {user_input[CONF_HOST]} (slave {user_input[CONF_SLAVE]})"
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): int,
                vol.Required(CONF_DEVICE, default=DEVICE_MINI): vol.In([DEVICE_MINI, DEVICE_MEGA]),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
