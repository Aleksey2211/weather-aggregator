from .geo_point import CityModel


def check_geo_point(data: dict, model: CityModel) ->  CityModel|dict:
    try:
        city_info = model.model_validate(data)
        return city_info

    except Exception as e:  # Ловим неожиданные ошибки (например, тип данных)
        return {"massage" :"no such city"}
