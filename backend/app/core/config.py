from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+aiosqlite:///./app.db", alias="DATABASE_URL")
    secret_key: str = Field(default="devsecret", alias="SECRET_KEY")
    upload_dir: Path = Field(default=Path("./uploads").resolve(), alias="UPLOAD_DIR")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()