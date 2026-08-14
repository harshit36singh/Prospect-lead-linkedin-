from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BACKEND_DIR / ".env"), extra="ignore")

    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'prospectlead.db').as_posix()}"
    seed_companies_path: Path = BACKEND_DIR / "data" / "seed_companies.json"
    reports_dir: Path = BACKEND_DIR / "reports"

    github_token: str | None = None
    google_service_account_json: str | None = None

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
settings.reports_dir.mkdir(parents=True, exist_ok=True)
(BACKEND_DIR / "data").mkdir(parents=True, exist_ok=True)
