"""A small client for the local wger API (M3: log in and read).

wger stores the client's program and training log. The server talks to it with the client's personal API key
(header `Authorization: Token <key>`), kept in .env and never in code or git.
"""

from pathlib import Path

import httpx
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class WgerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_prefix="WGER_", extra="ignore")

    url: str = "http://localhost:8020"
    api_key: SecretStr  # SecretStr: printed as '**********', so the key never ends up in a log by accident


class WgerUnavailable(Exception):
    """wger isn't running or didn't answer."""


class WgerClient:
    def __init__(self, settings: WgerSettings | None = None, timeout: float = 15.0):
        s = settings or WgerSettings()
        self._http = httpx.Client(base_url=f"{s.url}/api/v2/", timeout=timeout,
                                  headers={"Authorization": f"Token {s.api_key.get_secret_value()}",
                                           "Accept": "application/json"})

    def get(self, path: str, **params) -> dict:
        try:
            r = self._http.get(path, params=params)
        except httpx.TransportError as e:
            raise WgerUnavailable("Can't reach wger. Is it running? Start it with: cd ~/wger-docker && docker compose up -d") from e
        r.raise_for_status()
        return r.json()

    def me(self) -> dict:
        """The account this key belongs to (proves the login works)."""
        return self.get("userprofile/")

    def routines(self) -> list[dict]:
        return self.get("routine/")["results"]
