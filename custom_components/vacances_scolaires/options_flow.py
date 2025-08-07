from __future__ import annotations

from typing import Any
import voluptuous as vol
import logging
from homeassistant.config_entries import OptionsFlow, ConfigEntry
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    CONF_VERIFY_SSL,
)

_LOGGER = logging.getLogger(__name__)

class VacancesScolairesOptionsFlowHandler(OptionsFlowWithConfigEntry):

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        super().__init__()
        self.config_entry = config_entry 

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            old_options = self.config_entry.options
            
            if user_input.get(CONF_VERIFY_SSL) != old_options.get(CONF_VERIFY_SSL, True):
                _LOGGER.info(f"Option SSL changed from {old_options.get(CONF_VERIFY_SSL, True)} to {user_input.get(CONF_VERIFY_SSL)}")

            if user_input.get(CONF_UPDATE_INTERVAL) != old_options.get(CONF_UPDATE_INTERVAL,
                self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)):
                _LOGGER.info(f"Update interval changed from {old_options.get(CONF_UPDATE_INTERVAL, self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL))} to {user_input.get(CONF_UPDATE_INTERVAL)}")

            self.hass.config_entries.async_update_entry(self.config_entry, options=user_input)

            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL,
                        self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                    )
                ): int,
                vol.Optional(
                    CONF_VERIFY_SSL,
                    default=self.config_entry.options.get(
                        CONF_VERIFY_SSL,
                        self.config_entry.data.get(CONF_VERIFY_SSL, True)
                    )
                ): bool,
            })

        )

