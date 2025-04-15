"""Sensor platform for Vacances Scolaires."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, CONF_LOCATION, CONF_ZONE, CONF_CONFIG_TYPE, ATTRIBUTION, ATTR_START_DATE, ATTR_END_DATE, ATTR_DESCRIPTION, ATTR_LOCATION, ATTR_ZONE, ATTR_ANNEE_SCOLAIRE, ATTR_EN_VACANCES
from .coordinator import VacancesScolairesDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Vacances Scolaires sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VacancesScolairesSensor(coordinator, entry)], True)

class VacancesScolairesSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Vacances Scolaires sensor."""

    def __init__(self, coordinator: VacancesScolairesDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        config_type = entry.data.get(CONF_CONFIG_TYPE, "location")
        if config_type == "location":
            location = entry.data.get(CONF_LOCATION, "Unknown")
            self._attr_unique_id = f"{DOMAIN}_{config_type}_{location}"
            self._attr_name = f"Vacances Scolaires {location}"
        else:
            zone = entry.data.get(CONF_ZONE, "Unknown")
            self._attr_unique_id = f"{DOMAIN}_{config_type}_{zone}"
            self._attr_name = f"Vacances Scolaires {zone}"
        self._attr_attribution = ATTRIBUTION

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("state") if self.coordinator.data else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            return {
                ATTR_START_DATE: self.coordinator.data.get("start_date"),
                ATTR_END_DATE: self.coordinator.data.get("end_date"),
                ATTR_DESCRIPTION: self.coordinator.data.get("description"),
                ATTR_LOCATION: self.coordinator.data.get("location"),
                ATTR_ZONE: self.coordinator.data.get("zone"),
                ATTR_ANNEE_SCOLAIRE: self.coordinator.data.get("année_scolaire"),
                ATTR_EN_VACANCES: self.coordinator.data.get("on_vacation")
            }
        return {}
