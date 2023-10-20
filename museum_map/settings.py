"""Application configuration settings."""
import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings
from yaml import safe_load


class InitSettings(BaseSettings):
    """Initial settings for loading the configuration."""

    config_path: str = "./"


class DatabaseSettings(BaseModel):
    """Settings for the database."""

    dsn: str


class Settings(BaseModel):
    """Application settings."""

    db: DatabaseSettings


init_settings = InitSettings()
with open(os.path.join(init_settings.config_path, "config.yml")) as config_file:
    settings = Settings(**safe_load(config_file))
