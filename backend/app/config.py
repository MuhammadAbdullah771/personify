import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine the absolute path to the backend/.env file (parent directory of app/)
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
env_file_path = os.path.join(backend_dir, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(env_file_path, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str = ""
    supabase_key: str = ""
    match_distance_threshold: float = 0.6
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", "8000"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
