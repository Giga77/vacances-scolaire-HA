from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from datetime import datetime
from zoneinfo import ZoneInfo
from .const import DOMAIN

class VacancesScolairesCalendar(CoordinatorEntity, CalendarEntity):
    """Vacances Scolaires Calendar class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._attr_name = f"Vacances Scolaires {config_entry.title}"
        self._attr_unique_id = f"{config_entry.entry_id}_calendar"
        self._timezone = None

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        self._timezone = ZoneInfo(self.hass.config.time_zone)

    @property
    def event(self):
        """Return the next upcoming event."""
        if self.coordinator.data["on_vacation"]:
            return CalendarEvent(
                start=datetime.fromisoformat(self.coordinator.data["start_date"]).replace(tzinfo=self._timezone),
                end=datetime.fromisoformat(self.coordinator.data["end_date"]).replace(tzinfo=self._timezone),
                summary=self.coordinator.data["description"]
            )
        return None

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        events = []
        if self.coordinator.data["on_vacation"]:
            event_start = datetime.fromisoformat(self.coordinator.data["start_date"]).replace(tzinfo=self._timezone)
            event_end = datetime.fromisoformat(self.coordinator.data["end_date"]).replace(tzinfo=self._timezone)
            if start_date <= event_end and end_date >= event_start:
                events.append(self.event)
        return events

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Vacances Scolaires Calendar platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VacancesScolairesCalendar(coordinator, config_entry)], True)
