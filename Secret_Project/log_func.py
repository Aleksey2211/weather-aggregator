from .shemas import RequestLog
from fastapi.requests import Request
import uuid


def log_request(city: str, country: str, request: Request) -> RequestLog:
    """Собирает данные из запроса и возвращает модель."""
    return RequestLog(
        city=city,
        country_code=country,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
        user_country=None,
        user_city=None,
        response_status=200,
        request_id=str(uuid.uuid4())[:8]
        )