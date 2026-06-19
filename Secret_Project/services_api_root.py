from typing import Dict
from pydantic import BaseModel, Field


OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
SEVENTIMER_API_URL = "http://www.7timer.info/bin/api.pl?lat={lat}&lon={lon}&product=civil&output=json"
NASA_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,RH2M&community=RE&longitude={lon}&latitude={lat}&start=20230101&end=20230101&format=JSON"


# ============================================
# 1. КОНФИГУРАЦИЯ СЕРВИСОВ
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
        url_template=OPEN_METEO_API_URL,
        parser_class="OpenMeteoParser",
        enabled=True,
        timeout_seconds=10,
        units={"temperature": "°C", "wind_speed": "km/h"},
    ),
    "www.7timer.info": ServiceConfig(
        name="www.7timer.info",
        url_template=SEVENTIMER_API_URL,
        parser_class="SevenTimerParser",
        enabled=True,
        timeout_seconds=15,
        units={"temperature": "°C", "wind_speed": "m/s"},
    ),
    "power.larc.nasa.gov": ServiceConfig(
        name="power.larc.nasa.gov",
        url_template=NASA_API_URL,
        parser_class="NasaPowerParser",
        enabled=True,
        timeout_seconds=20,
        units={"temperature": "°C", "wind_speed": "m/s", "precipitation": "mm/day"},
    ),
}


