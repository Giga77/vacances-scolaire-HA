from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry, FlowResult
from homeassistant.helpers.entity_registry import async_get_registry
from homeassistant.core import HomeAssistant

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

def _build_user_schema(config_type: str = "location", data: dict = {}) -> vol.Schema:
    """Schema for initial config."""
    if config_type == "zone":
        return vol.Schema({
            vol.Required(CONF_CONFIG_TYPE, default="zone"): vol.In(["location", "zone"]),
            vol.Required(CONF_ZONE, default=data.get(CONF_ZONE, ZONE_OPTIONS[0])): vol.In(ZONE_OPTIONS),
            vol.Required(CONF_UPDATE_INTERVAL, default=data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): int,
            vol.Optional(CONF_CREATE_CALENDAR, default=data.get(CONF_CREATE_CALENDAR, False)): bool,
            vol.Required(CONF_API_SSL_CHECK, default=data.get(CONF_API_SSL_CHECK, True)): bool,
        })

    return vol.Schema({
        vol.Required(CONF_CONFIG_TYPE, default="location"): vol.In(["location", "zone"]),
        vol.Required(CONF_LOCATION, default=data.get(CONF_LOCATION, DEFAULT_LOCATION)): str,
        vol.Required(CONF_UPDATE_INTERVAL, default=data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): int,
        vol.Optional(CONF_CREATE_CALENDAR, default=data.get(CONF_CREATE_CALENDAR, False)): bool,
        vol.Required(CONF_API_SSL_CHECK, default=data.get(CONF_API_SSL_CHECK, True)): bool,
    })


def _build_options_schema(options: dict) -> vol.Schema:
    """Schema for options flow (no config_type, location or zone)."""
    return vol.Schema({
        vol.Required(CONF_UPDATE_INTERVAL, default=options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): int,
        vol.Optional(CONF_CREATE_CALENDAR, default=options.get(CONF_CREATE_CALENDAR, False)): bool,
        vol.Required(CONF_API_SSL_CHECK, default=options.get(CONF_API_SSL_CHECK, True)): bool,
    })


class VacancesScolairesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for Vacances Scolaires."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_CONFIG_TYPE, default="location"): vol.In(["location", "zone"]),
                }),
            )

        # Si l'utilisateur choisit 'location', aller à l'étape de localisation
        if user_input[CONF_CONFIG_TYPE] == "location":
            return await self.async_step_location()

        # Si l'utilisateur choisit 'zone', aller à l'étape de zone
        return await self.async_step_zone()

    async def async_step_location(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the location step."""
        errors = {}
        if user_input is not None:
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

    async def async_step_zone(self, user_input: dict[str, Any] | None = None) -> FlowResult:
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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return VacancesScolairesOptionsFlowHandler(config_entry)

class VacancesScolairesOptionsFlowHandler(OptionsFlow):
    """Handle Vacances Scolaires options."""

    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry
        self.entity_registry = None  # Initialisé après hass est prêt

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Show options form with only editable options."""
        if user_input is not None:
            # Accéder à self.hass ici lorsque l'instance est prête
            self.entity_registry = async_get_registry(self.hass)
            
            # Si le calendrier est désactivé, supprimer le calendrier
            if not user_input.get(CONF_CREATE_CALENDAR, False):
                # Suppression du calendrier si existant
                calendar_entity_id = f"calendar.{self.config_entry.entry_id}_vacances_scolaires"
                if self.entity_registry.async_is_registered(calendar_entity_id):
                    self.entity_registry.async_remove(calendar_entity_id)

            return self.async_create_entry(
                title="",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=_build_options_schema({**self.config_entry.data, **self.config_entry.options}),
        )
