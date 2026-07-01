from pydantic_settings import BaseSettings


from dotenv import load_dotenv
from pathlib import Path

# Загружаем .env из папки CONFIG
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / "CONFIG" / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

#    Auth_secret_one: str
#    Auth_secret_two: str


    class Config:
        env_file = "CONFIG/.env"  # путь к файлу окружения


settings = Settings()


DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"




