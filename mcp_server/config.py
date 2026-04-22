from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = "dev"
    log_level: str = "INFO"
    app_db_path: str = "application/data/abc_crm.db"


def load_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        app_db_path=os.getenv("APP_DB_PATH", "application/data/abc_crm.db"),
    )

