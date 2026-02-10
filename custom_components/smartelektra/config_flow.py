from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_COILS,
    CONF_DEVICE,
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE,
    DEFAULT_PORT,
    DEVICE_MEGA,
    DEVICE_MINI,
    DOMAIN,
    COILS_MEGA,
    COILS_MINI,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SLAVE, default=1): int,
        vol.Required(CONF_DEVICE, default=DEVICE_MINI): vol.In([DEVICE_MINI, DEVICE_MEGA]),
    }
)


class SmartElektraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = int(user_input[CONF_PORT])
            slave = int(user_input[CONF_SLAVE])
            device = user_input[CONF_DEVICE]

            coils = COILS_MINI if device == DEVICE_MINI else COILS_MEGA

            unique = f"{host}:{port}:slave{slave}"
            await self.async_set_unique_id(unique)
            self._abort_if_unique_id_configured()

            data = {
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_SLAVE: slave,
                CONF_DEVICE: device,
                CONF_COILS: coils,
            }

            title = f"SmartElektra {host} (slave {slave})"
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SmartElektraOptionsFlowHandler(config_entry)


class SmartElektraOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE, default=self.config_entry.data.get(CONF_DEVICE, DEVICE_MINI)): vol.In(
                    [DEVICE_MINI, DEVICE_MEGA]
                ),
            }
        )

        if user_input is not None:
            device = user_input[CONF_DEVICE]
            coils = COILS_MINI if device == DEVICE_MINI else COILS_MEGA

            # Options can override device/coils without re-creating the entry
            return self.async_create_entry(
                title="",
                data={
                    CONF_DEVICE: device,
                    CONF_COILS: coils,
                },
            )

        return self.async_show_form(step_id="init", data_schema=schema)
