from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN, PLATFORMS, CONF_CREATE_CALENDAR
from .coordinator import VacancesScolairesDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vacances Scolaires from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = VacancesScolairesDataUpdateCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        raise ConfigEntryNotReady("Failed to fetch initial data from Vacances Scolaires API")

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Use async_forward_entry_setups instead of async_forward_entry_setup
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if entry.data.get(CONF_CREATE_CALENDAR):
        await hass.config_entries.async_forward_entry_setup(entry, "calendar")

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
