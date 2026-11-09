import json
from urllib.error import HTTPError

import pytest

import api_client


class FakeResponse:
    status = 200
    reason = "OK"

    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self) -> bytes:
        return self.body


def test_fetch_post_returns_selected_fields(monkeypatch):
    body = json.dumps(
        {"id": 1, "title": "Sample title", "body": "Sample body", "userId": 7}
    ).encode("utf-8")
    response = FakeResponse(body)
    calls = []

    def fake_urlopen(url, timeout):
        calls.append((url, timeout))
        return response

    monkeypatch.setattr(api_client, "urlopen", fake_urlopen)

    result = api_client.fetch_post(1)

    assert result == {"id": 1, "title": "Sample title", "body": "Sample body"}
    assert calls == [("https://jsonplaceholder.typicode.com/posts/1", 10)]


def test_fetch_post_propagates_timeout(monkeypatch):
    def fake_urlopen(url, timeout):
        raise TimeoutError("request timed out")

    monkeypatch.setattr(api_client, "urlopen", fake_urlopen)

    with pytest.raises(TimeoutError, match="request timed out"):
        api_client.fetch_post(1)


def test_fetch_post_reports_http_error_status(monkeypatch):
    def fake_urlopen(url, timeout):
        raise HTTPError(url, 503, "Service Unavailable", None, None)

    monkeypatch.setattr(api_client, "urlopen", fake_urlopen)

    with pytest.raises(
        RuntimeError,
        match=r"Request failed with HTTP status 503: Service Unavailable",
    ):
        api_client.fetch_post(1)
