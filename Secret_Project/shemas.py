from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import Optional


# ============================================
# PYDANTIC V2 МОДЕЛЬ (в твоём стиле)
# ============================================
class RequestLog(BaseModel):
    """
    Модель для логирования запросов пользователей.
    """

    # Pydantic v2 конфигурация (как у CityModel)
    model_config = ConfigDict(
        extra="ignore",  # Игнорируем лишние поля
        populate_by_name=True,  # Можно использовать и название поля, и alias
        str_strip_whitespace=True,  # Убираем пробелы из строк
        validate_default=True,  # Валидируем значения по умолчанию
        json_schema_extra={
            "examples": [{
                "city": "Moscow",
                "country_code": "RU",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "referer": "https://google.com/search?q=weather+moscow",
                "user_country": "RU",
                "user_city": "Moscow",
                "timestamp": "2026-06-25T14:30:00Z",
                "response_status": 200,
                "request_id": "req_abc123"
            }]
        }
    )

    # Поля модели
    city: str = Field(..., description="Название города, который искал пользователь")
    country_code: Optional[str] = Field(None, description="Код страны (если указан в запросе)")
    ip_address: str = Field(..., description="IP-адрес пользователя")
    user_agent: Optional[str] = Field(None, description="User-Agent (браузер, устройство)")
    referer: Optional[str] = Field(None, description="Referer (откуда пришёл пользователь)")
    user_country: Optional[str] = Field(None, description="Страна пользователя по IP (например, RU, US)")
    user_city: Optional[str] = Field(None, description="Город пользователя по IP (если доступно)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Дата и время запроса (UTC)"
    )
    response_status: Optional[int] = Field(None, description="HTTP статус ответа")
    request_id: Optional[str] = Field(None, description="Уникальный ID запроса для отслеживания")