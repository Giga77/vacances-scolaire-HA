"""Config flow for Vacances Scolaires integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

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
                vol.Required(CONF_API_SSL_CHECK, default=True): bool,
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
                vol.Required(CONF_API_SSL_CHECK, default=True): bool,
            }),
            errors=errors
        )
class VacancesScolairesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flow for Vacances Scolaires."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the options configuration step."""
        if user_input is not None:
            # Si des données ont été fournies, on met à jour les options
            return self.async_create_entry(title="", data=user_input)

        # On récupère les options actuelles de la configuration
        current = self.config_entry.options

        # Affichage du formulaire pour modifier les options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_API_SSL_CHECK, default=current.get(CONF_API_SSL_CHECK, True)): bool,
                vol.Required(CONF_UPDATE_INTERVAL, default=current.get(CONF_UPDATE_INTERVAL, 12)): int,
            })
        )

async def async_get_options_flow(config_entry):
    """Retourne le gestionnaire d'options pour cette configuration."""
    return VacancesScolairesOptionsFlowHandler(config_entry)
