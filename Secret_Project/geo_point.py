from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional



class CityModel(BaseModel):
    # Поля модели
    name: str
    latitude: float
    longitude: float
    countrycode: str
    population: int
    timezone: str
    admin1code: Optional[str] = None
    alternatenames: List[str] = Field(default_factory=list)

    # Pydantic v2 конфигурация (современный стиль)
    model_config = ConfigDict(
        extra="ignore",  # Игнорируем лишние поля (geonameid и т.д.)
        populate_by_name=True,  # Можно использовать и название поля, и alias
        str_strip_whitespace=True,  # Убираем пробелы из строк
        validate_default=True,  # Валидируем значения по умолчанию
        json_schema_extra={  # Пример для документации
            "examples": [{
                "name": "Moscow",
                "latitude": 55.75222,
                "longitude": 37.61556,
                "countrycode": "RU",
                "population": 10381222,
                "timezone": "Europe/Moscow"
            }]
        }
    )

    # Валидатор для Pydantic v2
    @field_validator('name')
    @classmethod
    def capitalize_name(cls, v: str) -> str:
        return v.title() if v else v

    @field_validator('population')
    @classmethod
    def validate_population(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"Population cannot be negative: {v}")
        return v

    # Полезные методы
    # def __str__(self) -> str:
    #     return f"{self.name} ({self.countrycode}): {self.population:,} чел."

    @property
    def is_million_plus(self) -> bool:
        return self.population > 1_000_000


# Использование
city_dict = {
    'geonameid': 524901,  # будет проигнорировано
    'name': 'moscow',  # будет преобразовано в 'Moscow' валидатором
    'latitude': 55.75222,
    'longitude': 37.61556,
    'countrycode': 'RU',
    'population': 10381222,
    'timezone': 'Europe/Moscow',
    'admin1code': '48',
    'alternatenames': ['MOW', 'Maeskuy']
}



# Проверка на урезанный словарь
minimal_dict = {
    'name': 'Saint Petersburg',
    'latitude': 59.93428,
    'longitude': 30.3351,
    'countrycode': 'RU',
    'population': 5383890,
    'timezone': 'Europe/Moscow'
}

