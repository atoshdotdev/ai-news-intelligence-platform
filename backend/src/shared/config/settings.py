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


settings = Settings()
