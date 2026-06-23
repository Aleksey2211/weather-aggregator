from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Dict, Any
from forecast_response import get_weather_by_city
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

geo_app = FastAPI(title="Weather Aggregator API", description="API для получения погоды из нескольких источников")



templates = Jinja2Templates(directory="templates")
templates.env.cache = {}

geo_app.mount("/static", StaticFiles(directory="static"), name="static")

# Запрос на основную  страницу
@geo_app.get("/", response_class=HTMLResponse)
async def read_about_main(request: Request):
    return templates.TemplateResponse(request, "index.html", {})



@geo_app.get("/api/weather")
async def get_weather_api(
        city: str = Query(..., description="Название города", min_length=1, max_length=100),
        country: str = Query(None, description="Код страны (опционально)")
) -> Dict[str, Any]:
    """
    API для получения погоды (используется JavaScript)
    """
    try:
        result = get_weather_by_city(city, country)

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@geo_app.get("/health")
async def health_check() -> Dict[str, str]:
    """Проверка работоспособности API"""
    return {"status": "ok", "message": "Weather Aggregator API is running"}


# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run("main:geo_app", host="127.0.0.1", port=8002,  reload=True)

print( BASE_DIR )