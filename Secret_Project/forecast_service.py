import weakref
import requests
from typing import Dict
from services_api_root  import OPEN_METEO_API_URL, SEVENTIMER_API_URL, NASA_API_URL


class ForecastServer:

    _instances = weakref.WeakSet()

    def __init__(self, id: int, server_url_api: str):
        self.id = id
        self.server_url_api = server_url_api
        ForecastServer._instances.add(self)

    @classmethod
    def get_instances(cls) -> list:
        return list(cls._instances)


open_meteo_var = ForecastServer(1, OPEN_METEO_API_URL )
seventimer_var = ForecastServer(2, SEVENTIMER_API_URL )
nasa_var = ForecastServer(3, NASA_API_URL )


def get_city_forecast(city, servers: list) -> Dict:
    try:
        forecast_dict = {}
        errors = {}
        countrycode = city.countrycode
        name = city.name
        lat = city.latitude
        lon = city.longitude


        for server in servers:
            server_name = server.server_url_api.split("/")[2]
            try:

                forecast_info = server.server_url_api.format(lat = lat, lon = lon)
                response = requests.get(forecast_info, timeout=10)
                weather = response.json()
                forecast_dict[server_name]= weather
            except Exception as e:
                errors[server_name] = str(e)

        return {
            "name" : name,
            "country_code" : countrycode,
            "forecasts" : forecast_dict,
            "errors" : errors
        }

    except AttributeError as e:
        return {"message": f"Incorrect city object: {e}"}
    except Exception as e:
        return {"message": f"Unexpected error: {e}"}

