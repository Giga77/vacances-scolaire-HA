from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN, PLATFORMS, CONF_CREATE_CALENDAR
from .coordinator import VacancesScolairesDataUpdateCoordinator
from .config_flow import VacancesScolairesOptionsFlowHandler

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vacances Scolaires from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = VacancesScolairesDataUpdateCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        raise ConfigEntryNotReady("Failed to fetch initial data from Vacances Scolaires API")

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward platforms, including calendar if enabled
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if entry.data.get(CONF_CREATE_CALENDAR):
        await hass.config_entries.async_forward_entry_setups(entry, ["calendar"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Vacances Scolaires integration."""
    return True
