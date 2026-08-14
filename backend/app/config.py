from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BACKEND_DIR / ".env"), extra="ignore")

    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'prospectlead.db').as_posix()}"
    seed_companies_path: Path = BACKEND_DIR / "data" / "seed_companies.json"
    reports_dir: Path = BACKEND_DIR / "reports"

    # Deliberately NOT named GITHUB_TOKEN: that name is commonly already set in
    # a developer's shell (gh CLI, CI runners, editor extensions) for unrelated
    # purposes, and pydantic-settings reads the OS environment as a fallback.
    # Using a project-specific name avoids silently authenticating this app's
    # requests with a token the user never configured for it.
    github_token: str | None = Field(default=None, validation_alias="PROSPECTLEAD_GITHUB_TOKEN")
    google_service_account_json: str | None = None

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
settings.reports_dir.mkdir(parents=True, exist_ok=True)
(BACKEND_DIR / "data").mkdir(parents=True, exist_ok=True)
