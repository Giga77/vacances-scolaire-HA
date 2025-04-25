"""Config flow for Vacances Scolaires integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import HomeAssistant
import logging

from .const import (
    DOMAIN,
    CONF_LOCATION,
    CONF_ZONE,
    CONF_UPDATE_INTERVAL,
    CONF_CONFIG_TYPE,
    CONF_CREATE_CALENDAR,
    DEFAULT_LOCATION,
    DEFAULT_UPDATE_INTERVAL,
    CONF_VERIFY_SSL,
    ZONE_OPTIONS
)

_LOGGER = logging.getLogger(__name__)

class VacancesScolairesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vacances Scolaires."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_CONFIG_TYPE, default="location"): vol.In(["location", "zone"]),
                }),
            )

        if user_input[CONF_CONFIG_TYPE] == "location":
            return await self.async_step_location()
        else:
            return await self.async_step_zone()

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the location step."""
        errors = {}
        if user_input is not None:
            # Vous pouvez ajouter ici une validation pour la localisation si nécessaire
            return self.async_create_entry(
                title=f"Vacances Scolaires ({user_input[CONF_LOCATION]})",
                data={**user_input, CONF_CONFIG_TYPE: "location"}
            )

        return self.async_show_form(
            step_id="location",
            data_schema=vol.Schema({
                vol.Required(CONF_LOCATION, default=DEFAULT_LOCATION): str,
                vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
                vol.Optional(CONF_CREATE_CALENDAR, default=False): bool,
                vol.Optional(CONF_VERIFY_SSL, default=True): bool,
            }),
            errors=errors
        )

    async def async_step_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the zone step."""
        errors = {}
        if user_input is not None:
            zone = user_input[CONF_ZONE]
            if zone not in ZONE_OPTIONS:
                errors[CONF_ZONE] = "invalid_zone"
            else:
                return self.async_create_entry(
                    title=f"Vacances Scolaires ({zone})",
                    data={**user_input, CONF_CONFIG_TYPE: "zone"}
                )

        return self.async_show_form(
            step_id="zone",
            data_schema=vol.Schema({
                vol.Required(CONF_ZONE, default=ZONE_OPTIONS[0]): vol.In(ZONE_OPTIONS),
                vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
                vol.Optional(CONF_CREATE_CALENDAR, default=False): bool,
                vol.Optional(CONF_VERIFY_SSL, default=True): bool,
            }),
            errors=errors
        )
        
    # Ajout de l'OptionsFlow pour modifier update_interval et verify_ssl après configuration
    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return VacancesScolairesOptionsFlowHandler(config_entry)
        
class VacancesScolairesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Vacances Scolaires."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            old_options = self.config_entry.options
            
            if user_input.get(CONF_VERIFY_SSL) != old_options.get(CONF_VERIFY_SSL, True):
                _LOGGER.info(f"Option SSL changed from {old_options.get(CONF_VERIFY_SSL, True)} to {user_input.get(CONF_VERIFY_SSL)}")

            if user_input.get(CONF_UPDATE_INTERVAL) != old_options.get(CONF_UPDATE_INTERVAL, self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)):
                _LOGGER.info(f"Update interval changed from {old_options.get(CONF_UPDATE_INTERVAL, self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL))} to {user_input.get(CONF_UPDATE_INTERVAL)}")

            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_UPDATE_INTERVAL, default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL))): int,
                vol.Optional(CONF_VERIFY_SSL, default=self.config_entry.options.get(CONF_VERIFY_SSL, True)): bool,
            })
        )
