import http.client
import json
import threading
from contextlib import contextmanager

import pytest

from classic_cli_boardgames.web.server import create_server


@contextmanager
def run_server():
    try:
        server = create_server("127.0.0.1", 0)
    except OSError as exc:
        if getattr(exc, "errno", None) in {1, 13}:
            pytest.skip(f"Socket permissions prevent binding test server: {exc}")
        raise
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield host, port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def request_json(method, host, port, path, payload=None):
    headers = {}
    body = None
    if payload is not None:
        body = json.dumps(payload)
        headers["Content-Type"] = "application/json"
    connection = http.client.HTTPConnection(host, port, timeout=2)
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    data = response.read()
    content_type = response.getheader("Content-Type")
    connection.close()
    return response.status, data, content_type


def test_static_index_served() -> None:
    with run_server() as (host, port):
        status, data, content_type = request_json("GET", host, port, "/")
        assert status == 200
        assert content_type.startswith("text/html")
        assert b"Classic CLI Boardgames" in data


def test_api_session_lifecycle() -> None:
    with run_server() as (host, port):
        status, data, _ = request_json(
            "POST",
            host,
            port,
            "/api/session",
            {
                "game_key": "chess",
                "difficulty": "intermediate",
                "player_mode": "player",
            },
        )
        assert status == 200
        payload = json.loads(data)
        assert payload["ok"] is True
        session_id = payload["session"]["id"]

        status, data, _ = request_json(
            "POST",
            host,
            port,
            f"/api/session/{session_id}/action",
            {"type": "help"},
        )
        assert status == 200
        payload = json.loads(data)
        assert payload["ok"] is True
        assert "help" in payload["help"].lower()

        status, data, _ = request_json(
            "POST",
            host,
            port,
            f"/api/session/{session_id}/action",
            {"type": "end"},
        )
        assert status == 200
        payload = json.loads(data)
        assert payload["ok"] is True
        assert payload.get("ended") is True
