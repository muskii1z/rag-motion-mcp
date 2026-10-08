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
        self.base_url = s.url
        self._http = httpx.Client(base_url=f"{s.url}/api/v2/", timeout=timeout,
                                  headers={"Authorization": f"Token {s.api_key.get_secret_value()}",
                                           "Accept": "application/json"})

    def get(self, path: str, **params) -> dict:
        return self._send("GET", path, params=params).json()

    def _send(self, method: str, path: str, **kw) -> httpx.Response:
        try:
            r = self._http.request(method, path, **kw)
        except httpx.TransportError as e:
            raise WgerUnavailable("Can't reach wger. Is it running? Start it with: cd ~/wger-docker && docker compose up -d") from e
        if r.is_error:  # include wger's reason (e.g. which field it rejected) in the error
            raise httpx.HTTPStatusError(f"{method} {path} -> {r.status_code}: {r.text[:300]}", request=r.request, response=r)
        return r

    def post(self, path: str, data: dict) -> dict:
        return self._send("POST", path, json=data).json()

    def delete(self, path: str) -> None:
        self._send("DELETE", path)

    def list_all(self, path: str, **params) -> list[dict]:
        """Every row of a list endpoint (wger pages them; limit is capped at 999)."""
        rows, offset = [], 0
        while True:
            page = self.get(path, limit=999, offset=offset, **params)
            rows += page["results"]
            if not page.get("next"):
                return rows
            offset += 999

    def routine_url(self, routine_id: int) -> str:
        return f"{self.base_url}/en/routine/{routine_id}/view"

    def me(self) -> dict:
        """The account this key belongs to (proves the login works)."""
        return self.get("userprofile/")

    def routines(self) -> list[dict]:
        return self.get("routine/")["results"]
