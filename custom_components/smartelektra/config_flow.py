import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_SLAVE, CONF_DEVICE, CONF_COILS

class SmartElektraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            device = user_input[CONF_DEVICE]
            user_input[CONF_COILS] = 7 if device == "mini" else 30
            return self.async_create_entry(
                title=f"SmartElektra {user_input[CONF_HOST]} (slave {user_input[CONF_SLAVE]})",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=502): int,
                vol.Required(CONF_SLAVE, default=1): int,
                vol.Required(CONF_DEVICE, default="mini"): vol.In(["mini", "mega"]),
            }),
        )
