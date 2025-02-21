"""Config flow for Vacances Scolaires integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_LOCATION, CONF_UPDATE_INTERVAL, DEFAULT_LOCATION, DEFAULT_UPDATE_INTERVAL

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vacances Scolaires."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_LOCATION, default=DEFAULT_LOCATION): str,
                        vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
                    }
                ),
            )

        return self.async_create_entry(title="Vacances Scolaires", data=user_input)
