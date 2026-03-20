"""
aetherlink/config.py — Application settings

Loads configuration from the .env file at the project root.
All values are read once at import time via pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Network
    host: str = "::"
    port: int = 58008

    # Security — optional here; auth.py raises 403 if empty at request time
    aether_key: str = ""  # set in .env; required for Phase 2 protected routes

    # Path map: loaded separately from path_map.json (see services/directory.py)
    path_map_file: str = "path_map.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Single shared instance imported everywhere
settings = Settings()
