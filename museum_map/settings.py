"""Application configuration settings."""

import logging
import logging.config
import os
from typing import Literal

from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from yaml import safe_load


class InitSettings(BaseSettings):
    """Initial settings for loading the configuration."""

    config_path: str = "./"
    images_path: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class DatabaseSettings(BaseModel):  # TODO: Need to refactor this into the InitSettings
    """Settings for the database."""

    dsn: str


class AppFooter(BaseModel):
    """The settings for a single footer."""

    label: str
    url: str


class AppFooters(BaseModel):
    """The settings for the UI footers."""

    center: AppFooter
    right: AppFooter


class AppItemMetadata(BaseModel):
    """The settings for a single item metadata field."""

    name: str
    label: str


class AppItems(BaseModel):
    """The settings for the item configuration."""

    texts: list[AppItemMetadata]
    fields: list[AppItemMetadata]


class AppSettings(BaseModel):
    """The web application settings."""

    base_url: str
    intro: str
    footer: AppFooters
    item: AppItems


class DataHierarchySettings(BaseModel):
    """The data hierarchy settings."""

    field: str
    expansions: list[str]


class RoomPosition(BaseModel):
    """The layout position of a room."""

    x: int
    y: int
    width: int
    height: int


class RoomSettings(BaseModel):
    """The individual room settings."""

    id: str
    direction: Literal["vert"] | Literal["horiz"]
    items: int
    splits: int
    position: RoomPosition


class LayoutSettings(BaseModel):
    """The layout settings."""

    rooms: list[RoomSettings]


class DataSettings(BaseModel):
    """The data settings."""

    topic_fields: list[str]
    hierarchy: DataHierarchySettings
    year_field: str


class SearchSettings(BaseModel):
    """The search index settings."""

    url: HttpUrl
    key: str


class Settings(BaseModel):
    """Application settings."""

    app: AppSettings
    data: DataSettings
    db: DatabaseSettings
    search: SearchSettings
    layout: LayoutSettings


init_settings = InitSettings()
if os.path.exists(os.path.join(init_settings.config_path, "config.yml")):
    with open(os.path.join(init_settings.config_path, "config.yml")) as config_file:
        settings = Settings(**safe_load(config_file))
else:
    settings = Settings()

if os.path.exists(os.path.join(init_settings.config_path, "logging.yaml")):
    with open(os.path.join(init_settings.config_path, "logging.yaml")) as config_file:
        logging.config.dictConfig(safe_load(config_file))
