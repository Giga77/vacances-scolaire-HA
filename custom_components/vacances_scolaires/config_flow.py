from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry, FlowResult

from .const import (
    DOMAIN,
    CONF_LOCATION,
    CONF_ZONE,
    CONF_UPDATE_INTERVAL,
    CONF_CONFIG_TYPE,
    CONF_CREATE_CALENDAR,
    DEFAULT_LOCATION,
    DEFAULT_UPDATE_INTERVAL,
    CONF_API_SSL_CHECK,
    ZONE_OPTIONS
)


def _build_schema(data: dict, options: dict) -> vol.Schema:
    """Helper to build the schema for user/options form."""
    config_type = data.get(CONF_CONFIG_TYPE, "location")
    schema = {}

    if config_type == "location":
        schema = {
            vol.Required(CONF_CONFIG_TYPE, default="location"): vol.In(["location", "zone"]),
            vol.Required(CONF_LOCATION, default=data.get(CONF_LOCATION, DEFAULT_LOCATION)): str,
        }
    else:
        schema = {
            vol.Required(CONF_CONFIG_TYPE, default="zone"): vol.In(["location", "zone"]),
            vol.Required(CONF_ZONE, default=data.get(CONF_ZONE, ZONE_OPTIONS[0])): vol.In(ZONE_OPTIONS),
        }

    schema.update({
        vol.Required(CONF_UPDATE_INTERVAL, default=options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): int,
        vol.Optional(CONF_CREATE_CALENDAR, default=options.get(CONF_CREATE_CALENDAR, False)): bool,
        vol.Required(CONF_API_SSL_CHECK, default=options.get(CONF_API_SSL_CHECK, True)): bool,
    })

    return vol.Schema(schema)


class VacancesScolairesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Vacances Scolaires."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle user input."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Vacances Scolaires ({user_input.get(CONF_LOCATION, user_input.get(CONF_ZONE, 'France'))})",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema({}, {}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return VacancesScolairesOptionsFlowHandler(config_entry)


class VacancesScolairesOptionsFlowHandler(OptionsFlow):
    """Handle Vacances Scolaires options."""

    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the options flow."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(self.config_entry.data, self.config_entry.options),
        )
