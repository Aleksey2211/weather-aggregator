import abc
import logging
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


#from forecast_service import work
# ============================================
# 1. НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ============================================
# 1. ЕДИНАЯ PYDANTIC V2 МОДЕЛЬ
# ============================================

class WeatherData(BaseModel):
    """Унифицированная структура данных о погоде."""

    temperature_c: Optional[float] = Field(None, description="Температура в °C")
    wind_speed_kmh: Optional[float] = Field(None, description="Скорость ветра в км/ч")
    wind_direction_deg: Optional[int] = Field(
        None, description="Направление ветра в градусах (0-360)"
    )
    precipitation_mm: Optional[float] = Field(
        None, description="Количество осадков в мм"
    )
    cloud_cover_pct: Optional[int] = Field(None, description="Облачность в % (0-100)")
    source_name: str = Field(..., description="Имя источника данных")
    raw_data_info: str = Field("no info", description="Информация о сырых данных")

    model_config = ConfigDict(
        use_enum_values=True,
        str_strip_whitespace=True,
        validate_default=True,
        extra="ignore",
    )

# ============================================
# 2. КОНФИГУРАЦИЯ СЕРВИСОВ
# ============================================
class ServiceConfig(BaseModel):
    """Конфигурация одного сервиса погоды."""

    name: str
    url_template: str
    parser_class: str
    enabled: bool = True
    timeout_seconds: int = 10
    retry_count: int = 3
    units: Dict[str, str] = Field(default_factory=dict)


SERVICES_CONFIG: Dict[str, ServiceConfig] = {
    "api.open-meteo.com": ServiceConfig(
        name="api.open-meteo.com",
        url_template="https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
        parser_class="OpenMeteoParser",
        enabled=True,
        timeout_seconds=10,
        units={"temperature": "°C", "wind_speed": "km/h"},
    ),
    "www.7timer.info": ServiceConfig(
        name="www.7timer.info",
        url_template="http://www.7timer.info/bin/api.pl?lat={lat}&lon={lon}&product=civil&output=json",
        parser_class="SevenTimerParser",
        enabled=True,
        timeout_seconds=15,
        units={"temperature": "°C", "wind_speed": "m/s"},
    ),
    "power.larc.nasa.gov": ServiceConfig(
        name="power.larc.nasa.gov",
        url_template="https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,WS2M,WD2M,PRECTOTCORR,CLOUD_AMT&community=RE&longitude={lon}&latitude={lat}&start=20230101&end=20230101&format=JSON",
        parser_class="NasaPowerParser",
        enabled=True,
        timeout_seconds=20,
        units={"temperature": "°C", "wind_speed": "m/s", "precipitation": "mm/day"},
    ),
}


# ============================================
# 3. АБСТРАКТНЫЙ БАЗОВЫЙ КЛАСС (СТРАТЕГИЯ)
# ============================================
class WeatherParser(abc.ABC):
    """Абстрактный парсер погоды."""

    @abc.abstractmethod
    def parse(self, raw_data: Dict[str, Any]) -> WeatherData:
        pass


# ============================================
# 4. ПАРСЕР OPEN-METEO
# ============================================
class OpenMeteoParser(WeatherParser):
    """Парсер для API Open-Meteo."""

    def parse(self, raw_data: Dict[str, Any]) -> WeatherData:
        logger.debug("OpenMeteoParser: начат парсинг")

        current = raw_data.get("current_weather", {})

        result = WeatherData(
            temperature_c=current.get("temperature"),
            wind_speed_kmh=current.get("windspeed"),
            wind_direction_deg=current.get("winddirection"),
            precipitation_mm=None,
            cloud_cover_pct=None,
            source_name="open-meteo",
        )

        logger.info(
            f"OpenMeteoParser: температура={result.temperature_c}°C, ветер={result.wind_speed_kmh}км/ч"
        )
        return result


# ============================================
# 5. ПАРСЕР 7TIMER
# ============================================
class SevenTimerParser(WeatherParser):
    """Парсер для API 7Timer."""

    _DIRECTION_TO_DEGREES = {
        "N": 0,
        "NNE": 22.5,
        "NE": 45,
        "ENE": 67.5,
        "E": 90,
        "ESE": 112.5,
        "SE": 135,
        "SSE": 157.5,
        "S": 180,
        "SSW": 202.5,
        "SW": 225,
        "WSW": 247.5,
        "W": 270,
        "WNW": 292.5,
        "NW": 315,
        "NNW": 337.5,
    }

    @classmethod
    def _convert_wind_direction(cls, direction_str: Optional[str]) -> Optional[int]:
        if not direction_str:
            return None
        return cls._DIRECTION_TO_DEGREES.get(direction_str.upper())

    @classmethod
    def _convert_cloud_cover(cls, cloud_value: Optional[int]) -> Optional[int]:
        if cloud_value is None:
            return None
        if cloud_value == 9:
            return 100
        return int(round((cloud_value / 8.0) * 100))

    def parse(self, raw_data: Dict[str, Any]) -> WeatherData:
        logger.debug("SevenTimerParser: начат парсинг")

        dataseries = raw_data.get("dataseries", [])
        if not dataseries:
            logger.error("SevenTimerParser: отсутствует поле 'dataseries'")
            return WeatherData(source_name="7timer", raw_data_info="no data series")

        forecast = dataseries[0]
        wind_info = forecast.get("wind10m", {})

        wind_speed_ms = wind_info.get("speed")
        wind_speed_kmh = wind_speed_ms * 3.6 if wind_speed_ms is not None else None
        wind_dir_deg = self._convert_wind_direction(wind_info.get("direction"))

        precip = forecast.get("prec_amount")
        precip_mm = precip if precip is not None and precip > 0 else None
        cloud_pct = self._convert_cloud_cover(forecast.get("cloudcover"))

        result = WeatherData(
            temperature_c=forecast.get("temp2m"),
            wind_speed_kmh=wind_speed_kmh,
            wind_direction_deg=wind_dir_deg,
            precipitation_mm=precip_mm,
            cloud_cover_pct=cloud_pct,
            source_name="7timer",
        )

        logger.info(
            f"SevenTimerParser: температура={result.temperature_c}°C, "
            f"ветер={result.wind_speed_kmh}км/ч, дождь={result.precipitation_mm}мм"
        )
        return result


# ============================================
# 6. ПАРСЕР NASA POWER
# ============================================
class NasaPowerParser(WeatherParser):
    """Парсер для NASA POWER API."""

    def parse(self, raw_data: Dict[str, Any]) -> WeatherData:
        logger.debug("NasaPowerParser: начат парсинг")

        parameters = raw_data.get("properties", {}).get("parameter", {})

        def _get_first_value(param_dict: Dict) -> Optional[Union[float, int]]:
            if not param_dict:
                return None
            first_key = next(iter(param_dict))
            return param_dict.get(first_key)

        temp_c = _get_first_value(parameters.get("T2M", {}))
        wind_speed_ms = _get_first_value(parameters.get("WS2M", {}))
        wind_speed_kmh = wind_speed_ms * 3.6 if wind_speed_ms is not None else None
        wind_dir_deg = _get_first_value(parameters.get("WD2M", {}))
        precip_mm = _get_first_value(parameters.get("PRECTOTCORR", {}))
        cloud_pct = _get_first_value(parameters.get("CLOUD_AMT", {}))

        result = WeatherData(
            temperature_c=temp_c,
            wind_speed_kmh=wind_speed_kmh,
            wind_direction_deg=wind_dir_deg if isinstance(wind_dir_deg, int) else None,
            precipitation_mm=precip_mm if isinstance(precip_mm, (int, float)) else None,
            cloud_cover_pct=cloud_pct if isinstance(cloud_pct, (int, float)) else None,
            source_name="nasa-power",
        )

        logger.info(
            f"NasaPowerParser: температура={result.temperature_c}°C, "
            f"ветер={result.wind_speed_kmh}км/ч, дождь={result.precipitation_mm}мм"
        )
        return result


# ============================================
# 7. ФАБРИКА (СТРАТЕГИЯ)
# ============================================
class ParserFactory:
    """Фабрика, возвращающая нужный парсер на основе имени источника."""

    _parsers = {
        "api.open-meteo.com": OpenMeteoParser(),
        "www.7timer.info": SevenTimerParser(),
        "power.larc.nasa.gov": NasaPowerParser(),
    }

    @classmethod
    def get_parser(cls, source_name: str) -> Optional[WeatherParser]:
        parser = cls._parsers.get(source_name)
        if parser:
            logger.debug(f"ParserFactory: выбран парсер для {source_name}")
        else:
            logger.warning(f"ParserFactory: парсер для {source_name} не найден")
        return parser


# ============================================
# 8. ФУНКЦИЯ-ОРКЕСТРАТОР (ОДИН СЕРВИС)
# ============================================
def parse_weather_by_source(source_name: str, raw_data: Dict[str, Any]) -> WeatherData:
    """
    Парсит один источник.
    """
    logger.info(f"Запрос парсинга для источника: {source_name}")

    parser = ParserFactory.get_parser(source_name)
    if not parser:
        return WeatherData(
            source_name=source_name,
            raw_data_info=f"no parser available for {source_name}",
        )

    try:
        return parser.parse(raw_data)
    except Exception as e:
        logger.exception(f"Ошибка при парсинге {source_name}: {e}")
        return WeatherData(
            source_name=source_name, raw_data_info=f"parse error: {str(e)}"
        )


# ============================================
# 9. АГРЕГАТОР (ВСЕ СЕРВИСЫ)
# ============================================
def aggregate_all_forecasts(raw_aggregated_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Принимает сырой словарь со всеми сервисами.
    Возвращает словарь с парсингом для каждого сервиса.
    """
    parsed_forecasts = {}
    aggregation_errors = {}

    for source_name, raw_data in raw_aggregated_data.items():
        # Пропускаем служебные ключи
        if source_name in ("name", "country_code", "errors"):
            continue

        try:
            parsed = parse_weather_by_source(source_name, raw_data)
            parsed_forecasts[source_name] = parsed
        except Exception as e:
            aggregation_errors[source_name] = str(e)
            parsed_forecasts[source_name] = WeatherData(
                source_name=source_name, raw_data_info=f"aggregation error: {e}"
            )

    return {"forecasts": parsed_forecasts, "aggregation_errors": aggregation_errors}

