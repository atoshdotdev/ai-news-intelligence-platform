from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/ainews",
        description="The URL for the database connection",
    )
    ollama_url: str = Field(
        default="http://ollama:11434", description="The URL for the Ollama API"
    )
    web_crawler_url: str = Field(
        default="http://web-scraper:11235",
        description="The URL for the Web Crawler API",
    )
    web_crawler_sleep_seconds: int = Field(
        default=1800,
        description="The number of seconds the web crawler should sleep between cycles",
    )


settings = Settings()
