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

    @property
    def event(self):
        """Return the next upcoming event."""
        if self.coordinator.data["on_vacation"]:
            start_date = datetime.fromisoformat(self.coordinator.data["start_date"])
            end_date = datetime.fromisoformat(self.coordinator.data["end_date"])
            return CalendarEvent(
                start=start_date,
                end=end_date,
                summary=self.coordinator.data["description"],
                description=f"Du {start_date.strftime('%d/%m/%Y à %H:%M')} au {end_date.strftime('%d/%m/%Y à %H:%M')} (UTC)"
            )
        return None

    async def async_get_events(self, hass, start_date, end_date):
        """Get all events in a specific time frame."""
        events = []
        if self.coordinator.data["on_vacation"]:
            event_start = datetime.fromisoformat(self.coordinator.data["start_date"])
            event_end = datetime.fromisoformat(self.coordinator.data["end_date"])
            if start_date <= event_end and end_date >= event_start:
                event = CalendarEvent(
                    start=event_start,
                    end=event_end,
                    summary=self.coordinator.data["description"],
                    description=f"Du {event_start.strftime('%d/%m/%Y à %H:%M')} au {event_end.strftime('%d/%m/%Y à %H:%M')} (UTC)"
                )
                events.append(event)
        return events

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Vacances Scolaires Calendar platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([VacancesScolairesCalendar(coordinator, config_entry)], True)
