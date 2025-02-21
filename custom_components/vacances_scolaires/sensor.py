from datetime import datetime, timedelta
import logging
import aiohttp
import async_timeout
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, CONF_LOCATION, CONF_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Vacances Scolaires sensor platform."""
    location = entry.data[CONF_LOCATION]
    update_interval = entry.data[CONF_UPDATE_INTERVAL]

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
            _LOGGER.error(f"Error communicating with API: {err}")
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_data(self):
        """Fetch data from the API."""
        url = self._get_api_url()
        _LOGGER.debug(f"Fetching data from URL: {url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    _LOGGER.error(f"API returned status code {response.status}")
                    raise UpdateFailed(f"API returned status code {response.status}")

                data = await response.json()
                _LOGGER.debug(f"Raw API response: {data}")

                return self._process_data(data)

    def _get_api_url(self):
        """Generate the API URL."""
        today = datetime.now().strftime('%Y-%m-%d')
        return f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=end_date%3E%22{today}%22&order_by=end_date%20ASC&limit=1&refine=location%3A{self.location}"

    def _process_data(self, data):
        """Process API response and extract vacation data."""
        _LOGGER.debug(f"Processing data: {data}")

        results = data.get('results', [])

        if not results:
            _LOGGER.warning(f"No results found for location '{self.location}'.")
            return {"state": "Aucune donnée disponible", "attributes": {}}

        result = results[0]
        try:
            # Conversion ISO 8601 en date sans fuseau horaire
            start_date = datetime.fromisoformat(result['start_date']).date()
            end_date = datetime.fromisoformat(result['end_date']).date()
            today = datetime.now().date()

            if on_vacation: 
                state = f"{result['zones']} - Holidays"
            else:
                state = f"{result['zones']} - Work"
    
            return {
                "state": state,
                "attributes": {
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d'),
                    "description": result['description'],
                    "location": result['location'],
                    "zone": result['zones'],
                    "année scolaire": result['annee_scolaire'],
                    "on_vacation": on_vacation  # True si on est en vacances, sinon False
                }
            }

        except KeyError as e:
            _LOGGER.error(f"Missing key in API response: {e}")
            return {"state": "Données invalides", "attributes": {}}

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
