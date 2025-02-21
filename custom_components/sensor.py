"""Platform for sensor integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

import aiohttp
import async_timeout
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_LOCATION, CONF_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vacances Scolaires sensor platform."""
    location = config_entry.data[CONF_LOCATION]
    update_interval = config_entry.data[CONF_UPDATE_INTERVAL]

    coordinator = VacancesScolairesDataUpdateCoordinator(hass, location, update_interval)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([VacancesScolairesSensor(coordinator)], True)

class VacancesScolairesDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Vacances Scolaires data."""

    def __init__(self, hass, location, update_interval):
        """Initialize."""
        self.location = location
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=update_interval),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with async_timeout.timeout(10):
                return await self._fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_data(self):
        """Fetch data from the API."""
        url = self._get_api_url()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"API returned status code {response.status}")
                data = await response.json()
                return self._process_data(data)

    def _get_api_url(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=end_date%3E%22{today}%22&order_by=end_date%20ASC&limit=1&refine=location%3A{self.location}"

    def _process_data(self, data):
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            start_date = datetime.strptime(result['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(result['end_date'], '%Y-%m-%d').date()
            today = datetime.now().date()

            if start_date <= today <= end_date:
                state = f"{result['description']} jusqu'au {end_date.strftime('%d-%m-%Y')}"
            else:
                state = f"Prochaines : {result['description']} {start_date.strftime('%d-%m-%Y')}"

            return {
                "state": state,
                "attributes": {
                    "start_date": result['start_date'],
                    "end_date": result['end_date'],
                    "description": result['description']
                }
            }
        return {"state": "Aucune donnée disponible", "attributes": {}}

class VacancesScolairesSensor(SensorEntity):
    """Representation of a Vacances Scolaires sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Vacances Scolaires {self.coordinator.location}"

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return f"vacances_scolaires_{self.coordinator.location}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data["state"]

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self.coordinator.data["attributes"]

    @property
    def available(self):
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    async def async_update(self):
        """Update the entity."""
        await self.coordinator.async_request_refresh()
