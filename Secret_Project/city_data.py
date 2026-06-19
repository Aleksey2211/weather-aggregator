import geonamescache
from typing import Optional, Dict, Any

# Загрузка данных о городах
city_list = geonamescache.GeonamesCache(min_city_population=500)
cities = city_list.get_cities()
new_list_cities = list(cities.values())


def get_citydata(city: str = None, country_code: str = None) -> Optional[Dict[str, Any]]:
    """
    Поиск города по названию.
    Ищет в name, asciiname и alternatenames.
    """
    if not city:
        return None

    city_lower = city.lower().strip()

    for target_city in new_list_cities:
        # 1. Проверка по основному имени (Moskva)
        if target_city.get('name', '').lower() == city_lower:
            if country_code is None or target_city.get('countrycode') == country_code:
                return target_city

        # 2. Проверка по asciiname (Moskva)
        if target_city.get('asciiname', '').lower() == city_lower:
            if country_code is None or target_city.get('countrycode') == country_code:
                return target_city

        # 3. Проверка по альтернативным названиям (Moscow, Москва)
        alternates = target_city.get('alternatenames', [])
        for alt in alternates:
            if alt.lower() == city_lower:
                if country_code is None or target_city.get('countrycode') == country_code:
                    return target_city

    return None