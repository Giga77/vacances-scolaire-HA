"""Config flow for Vacances Scolaires integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_LOCATION, CONF_ZONE, CONF_UPDATE_INTERVAL, CONF_CONFIG_TYPE, DEFAULT_LOCATION, DEFAULT_UPDATE_INTERVAL

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
        if user_input is None:
            return self.async_show_form(
                step_id="location",
                data_schema=vol.Schema({
                    vol.Required(CONF_LOCATION, default=DEFAULT_LOCATION): str,
                    vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
                }),
            )

        return self.async_create_entry(
            title="Vacances Scolaires (Location)",
            data={**user_input, CONF_CONFIG_TYPE: "location"}
        )

    async def async_step_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the zone step."""
        ZONE_OPTIONS = ["Zone A", "Zone B", "Zone C"]
        if user_input is None:
            return self.async_show_form(
                step_id="zone",
                data_schema=vol.Schema({
                    vol.Required(CONF_ZONE, default=ZONE_OPTIONS[0]): vol.In(ZONE_OPTIONS),
                    vol.Required(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
                }),
            )

        return self.async_create_entry(
            title="Vacances Scolaires (Zone)",
            data={**user_input, CONF_CONFIG_TYPE: "zone"}
        )