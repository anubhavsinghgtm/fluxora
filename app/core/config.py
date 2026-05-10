from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    DB_HOSTNAME: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_NAME: str


    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.2
    GEMINI_MAX_OUTPUT_TOKENS: int = 100


    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )


    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOSTNAME}:{self.DB_PORT}/{self.DB_NAME}"



@lru_cache
def get_settings() -> Settings:
    return Settings()