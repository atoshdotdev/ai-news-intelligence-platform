from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/ainews",
        description="The URL for the database connection",
    )
    ollama_host: str = Field(
        default="http://ollama:11434/v1",
        description="The URL for the Ollama API",
    )
    web_crawler_url: str = Field(
        default="http://web-scraper:11235",
        description="The URL for the Web Crawler API",
    )
    web_crawler_sleep_seconds: int = Field(
        default=1800,
        description="The number of seconds the web crawler should sleep between cycles",
    )
    processing_sleep_seconds: int = Field(
        default=1800,
        description="The number of seconds the processing worker should sleep between cycles",
    )
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_expose_headers: list[str] = ["Content-Disposition"]


settings = Settings()
