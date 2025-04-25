import logging
from datetime import timedelta, date, datetime
from typing import Any
import asyncio
from aiohttp import ClientSession, TCPConnector, ClientError
import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry
from zoneinfo import ZoneInfo

from .const import DOMAIN, CONF_LOCATION, CONF_ZONE, CONF_API_SSL_CHECK, CONF_CONFIG_TYPE, CONF_UPDATE_INTERVAL, DEFAULT_LOCATION, ZONE_OPTIONS

_LOGGER = logging.getLogger(__name__)

# Fonction pour obtenir le fuseau horaire en fonction de la localisation
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

# Fonction pour traduire les mois en français
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
    """Classe pour gérer la mise à jour des données de Vacances Scolaires."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialisation du coordinateur de données."""
        self.entry = entry
        self.hass = hass
        self.api_ssl_check: bool = entry.options.get(CONF_API_SSL_CHECK, True)

        # Récupérer l'intervalle de mise à jour à partir des options, avec une valeur par défaut de 12 heures
        update_interval = entry.options.get(CONF_UPDATE_INTERVAL, entry.data.get(CONF_UPDATE_INTERVAL, 12))

        # Initialisation du parent avec l'intervalle de mise à jour
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=update_interval),
        )

    async def _create_session(self) -> ClientSession:
        """Créer une session aiohttp avec la vérification SSL optionnelle."""
        connector = TCPConnector(ssl=self.api_ssl_check)
        return ClientSession(connector=connector)

    async def _async_update_data(self) -> dict[str, Any]:
        """Récupérer les données depuis l'API."""
        today = date.today().isoformat()  # Date actuelle au format YYYY-MM-DD
        config_type = self.entry.options.get(CONF_CONFIG_TYPE, "location")

        # Construire l'URL de l'API en fonction du type de configuration (location ou zone)
        if config_type == "location":
            location = self.entry.options.get(CONF_LOCATION, DEFAULT_LOCATION)
            api_url = f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=end_date%3E%22{today}%22&order_by=start_date%20ASC&limit=1&refine=location%3A{location}"
        elif config_type == "zone":
            zone = self.entry.options.get(CONF_ZONE)
            if zone not in ZONE_OPTIONS:
                raise ValueError("La zone spécifiée n'est pas valide.")
            api_url = f"https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records?where=end_date%3E%22{today}%22&order_by=start_date%20ASC&limit=1&refine=zone%3A{zone}"
        else:
            raise ValueError("Le type de configuration est invalide.")
        
        try:
            # Effectuer une requête asynchrone avec un délai d'attente
            async with async_timeout.timeout(10):
                async with await self._create_session().get(api_url) as response:
                    response.raise_for_status()  # Si la réponse est une erreur, une exception sera levée
                    data = await response.json()  # Retourner les données JSON

                    # Vérification si des résultats sont retournés
                    if not data.get("records"):
                        raise UpdateFailed("Aucune donnée reçue de l'API")

                    result = data["records"][0]
                    start_date = datetime.fromisoformat(result['fields']['start_date']).replace(tzinfo=ZoneInfo("UTC"))
                    end_date = datetime.fromisoformat(result['fields']['end_date']).replace(tzinfo=ZoneInfo("UTC"))
                    today = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
                    on_vacation = start_date <= today <= end_date

                    state = "En vacances" if on_vacation else "Travail"
                    start_date_formatted = traduire_mois(start_date.strftime("%d %B %Y à %H:%M:%S %Z"))
                    end_date_formatted = traduire_mois(end_date.strftime("%d %B %Y à %H:%M:%S %Z"))

                    # Retourner les données
                    return {
                        "state": state,
                        "start_date": start_date_formatted,
                        "end_date": end_date_formatted,
                        "description": result['fields']['description'],
                        "location": result['fields']['location'],
                        "zone": result['fields']['zones'],
                        "année_scolaire": result['fields']['annee_scolaire'],
                        "on_vacation": on_vacation
                    }

        except asyncio.TimeoutError:
            raise UpdateFailed("Délai d'attente dépassé lors de la récupération des données de Vacances Scolaires.")
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Erreur lors de la communication avec l'API: {e}")
        except ValueError as e:
            raise UpdateFailed(f"Erreur dans la configuration: {e}")
        except Exception as e:
            _LOGGER.error("Erreur inattendue : %s", str(e))
            raise UpdateFailed(f"Erreur inconnue lors de la mise à jour des données : {e}")
