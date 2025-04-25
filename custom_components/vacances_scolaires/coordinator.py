from datetime import timedelta, date, datetime
import logging
from typing import Any
import asyncio
from zoneinfo import ZoneInfo
import aiohttp
import async_timeout
from aiohttp import ClientSession, TCPConnector
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_LOCATION, CONF_ZONE, CONF_API_SSL_CHECK, CONF_CONFIG_TYPE

_LOGGER = logging.getLogger(__name__)

def get_timezone(location):
    timezone_mapping = {
        "Guadeloupe": "America/Guadeloupe",
        "Guyane": "America/Cayenne",
        "Martinique": "America/Martinique",
        "Mayotte": "Indian/Mayotte",
        "Nouvelle Calédonie": "Pacific/Noumea",
        "Polynésie française": "Pacific/Tahiti",
        "Réunion": "Indian/Reunion",
        "Saint Pierre et Miquelon": "America/Miquelon",
        "Wallis et Futuna": "Pacific/Wallis"
    }
    return timezone_mapping.get(location, "Europe/Paris")

def traduire_mois(date_str: str) -> str:
    """Remplace les noms de mois en anglais par leur équivalent français."""
    mois_en = ["January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]
    mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin",
               "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

    for en, fr in zip(mois_en, mois_fr):
        date_str = date_str.replace(en, fr)

    return date_str

class VacancesScolairesDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Vacances Scolaires data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the data updater."""
        self.entry = entry
        self.config = {**entry.data, **entry.options}  # fusion data + options
        
        self.api_ssl_check: bool = self.config.get(CONF_API_SSL_CHECK, True)
        super().__init__(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_interval=timedelta(hours=self.config.get("update_interval", 12)),
        )
        
    
    async def _create_session(self) -> ClientSession:
        """Create aiohttp session with optional SSL verification."""
        connector = TCPConnector(ssl=self.api_ssl_check)
        return ClientSession(connector=connector)
        
    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""

        today = date.today().isoformat()
        config_type = self.config.get(CONF_CONFIG_TYPE, "location")
        if config_type == "location":
            location = self.config[CONF_LOCATION]
            api_url = f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=end_date%3E%22{today}%22&order_by=start_date%20ASC&limit=1&refine=location%3A{location}"
        elif config_type == "zone":
            zone = self.config[CONF_ZONE]
            api_url = f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=end_date%3E%22{today}%22&order_by=start_date%20ASC&limit=1&refine=zones%3A{zone}"
        else:
            raise UpdateFailed("Invalid configuration type")

        try:
            async with async_timeout.timeout(10):
                session = await self._create_session()
                try:
                    async with session.get(api_url) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error communicating with API: {response.status}")
                        data = await response.json()
        
                        if not data.get("results"):
                            raise UpdateFailed("No data received from API")
        
                        result = data["results"][0]
                        start_date = datetime.fromisoformat(result['start_date']).replace(tzinfo=ZoneInfo("UTC"))
                        end_date = datetime.fromisoformat(result['end_date']).replace(tzinfo=ZoneInfo("UTC"))
                        today = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
                        on_vacation = start_date <= today <= end_date
        
                        if on_vacation:
                            state = f"{result['zones']} - Holidays"
                        else:
                            state = f"{result['zones']} - Work"
        
                        start_date_formatted = traduire_mois(start_date.strftime("%d %B %Y à %H:%M:%S %Z"))
                        end_date_formatted = traduire_mois(end_date.strftime("%d %B %Y à %H:%M:%S %Z"))
        
                        return {
                            "state": state,
                            "start_date": start_date_formatted,
                            "end_date": end_date_formatted,
                            "description": result['description'],
                            "location": result['location'],
                            "zone": result['zones'],
                            "année_scolaire": result['annee_scolaire'],
                            "on_vacation": on_vacation
                        }
                finally:
                    await session.close()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
        except asyncio.TimeoutError:
            raise UpdateFailed("Timeout fetching Vacances Scolaires data")
