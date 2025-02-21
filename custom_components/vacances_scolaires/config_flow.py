"""Config flow for Vacances Scolaires integration."""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_LOCATION, CONF_UPDATE_INTERVAL, DEFAULT_LOCATION, DEFAULT_UPDATE_INTERVAL

class VacancesScolairesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vacances Scolaires."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(
                title="Vacances Scolaires",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_LOCATION, default=DEFAULT_LOCATION): str,
                vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
            }),
            errors=errors,
        )
