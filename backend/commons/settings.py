from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    poll_interval_minutes: int = 30
    posts_per_creator: int = 10
    instagram_creators: str = ""
    cors_origin: str = "http://localhost:5173"

    postgres_url: str | None = None
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str | None = None

    google_maps_api_key: str | None = None

    instagram_session_cookie: str | None = None
    instagram_username: str | None = None
    instagram_password: str | None = None

    openrouter_api_key: str | None = None

    @property
    def database_url(self) -> str:
        if self.postgres_url:
            return self.postgres_url
        if not (self.postgres_user and self.postgres_password and self.postgres_db):
            raise ValueError(
                "Please set either 'POSTGRES_URL' or the respective 'POSTGRES' environmental variables."
            )
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
