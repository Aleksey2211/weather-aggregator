from .city_data import  get_citydata
from .load_geo_point import check_geo_point
from .geo_point import CityModel
from .forecast_service import ForecastServer, get_city_forecast
from .weather_parsers import aggregate_all_forecasts


def get_weather_by_city(city_name: str, country_code: str = None) -> dict:
    """
    Единая точка входа для FastAPI ручки.

    Аргументы:
        city_name: название города
        country_code: код страны (опционально)

    Возвращает:
        dict с погодой от всех сервисов
    """
    # 1. Поиск города в geonamescache
    city_data = get_citydata(city=city_name, country_code=country_code)

    if not city_data:
        return {"error": f"City '{city_name}' not found"}

    # 2. Валидация через Pydantic
    city = check_geo_point(city_data, CityModel)

    if isinstance(city, dict) and "massage" in city:
        return {"error": f"Invalid city data for '{city_name}'"}

    # 3. Сбор сырых данных со всех серверов
    work_servers = ForecastServer.get_instances()
    raw_data = get_city_forecast(city, work_servers)

    # 4. Парсинг и агрегация
    result = aggregate_all_forecasts(raw_data["forecasts"])

    # 5. Возвращаем результат с метаданными города
    return {
        "name": raw_data["name"],
        "country_code": raw_data["country_code"],
        "forecasts": result["forecasts"],
        "aggregation_errors": result["aggregation_errors"],
        "fetch_errors": raw_data["errors"]
    }