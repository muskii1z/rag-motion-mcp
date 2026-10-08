"""The wger client, offline: httpx's MockTransport plays wger."""

import httpx
import pytest

from rag_motion_mcp.wger import WgerClient, WgerSettings, WgerUnavailable


def client_with(handler) -> WgerClient:
    w = WgerClient(WgerSettings(url="http://wger.test", api_key="k123"))
    w._http = httpx.Client(base_url="http://wger.test/api/v2/", transport=httpx.MockTransport(handler),
                           headers=w._http.headers)
    return w


def test_sends_the_api_key_as_a_token_header():
    seen = {}
    def handler(request):
        seen["auth"] = request.headers["Authorization"]
        return httpx.Response(200, json={"username": "sarah_demo"})
    assert client_with(handler).me()["username"] == "sarah_demo"
    assert seen["auth"] == "Token k123"


def test_key_is_hidden_when_settings_are_printed():
    assert "k123" not in repr(WgerSettings(url="http://wger.test", api_key="k123"))


def test_a_wrong_key_raises_and_a_down_server_gives_a_clear_message():
    with pytest.raises(httpx.HTTPStatusError):
        client_with(lambda r: httpx.Response(403, json={"detail": "Invalid token."})).me()
    def down(request):
        raise httpx.ConnectError("refused")
    with pytest.raises(WgerUnavailable, match="docker compose up"):
        client_with(down).me()
