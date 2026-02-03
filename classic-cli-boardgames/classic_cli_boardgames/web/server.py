"""Local HTTP server for the Classic CLI Boardgames web UI."""

from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
import argparse
import json
from typing import Any, Mapping, Optional
from urllib.parse import urlparse

from classic_cli_boardgames.web.sessions import SESSION_STORE

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


class WebHandler(BaseHTTPRequestHandler):
    server_version = "ClassicCLIWeb/1.0"

    def do_GET(self) -> None:  # noqa: N802 - match BaseHTTPRequestHandler
        path = urlparse(self.path).path
        if path == "/api/options":
            self._send_json(SESSION_STORE.list_options())
            return
        if self._serve_static(path):
            return
        self._send_json(
            {"ok": False, "error": "Not found."},
            status=HTTPStatus.NOT_FOUND,
        )

    def do_POST(self) -> None:  # noqa: N802 - match BaseHTTPRequestHandler
        path = urlparse(self.path).path
        if path == "/api/session":
            payload = self._read_json_payload()
            if payload is None:
                return
            game_key = (payload.get("game_key") or payload.get("game") or "").strip()
            difficulty_key = _optional_text(payload.get("difficulty"))
            mode_key = _optional_text(payload.get("player_mode"))
            seed = _parse_seed(payload.get("seed"))
            if seed is False:
                self._send_json(
                    {"ok": False, "error": "Seed must be an integer."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            try:
                session = SESSION_STORE.create_session(
                    game_key=game_key,
                    difficulty_key=difficulty_key,
                    mode_key=mode_key,
                    seed=seed if isinstance(seed, int) else None,
                )
            except ValueError:
                self._send_json(
                    {"ok": False, "error": "Unknown game."},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            self._send_json({"ok": True, "session": session})
            return

        session_id = _session_id_from_action_path(path)
        if session_id:
            payload = self._read_json_payload()
            if payload is None:
                return
            try:
                result = SESSION_STORE.handle_action(session_id, payload)
            except KeyError:
                self._send_json(
                    {"ok": False, "error": "Session not found."},
                    status=HTTPStatus.NOT_FOUND,
                )
                return
            status = (
                HTTPStatus.OK if result.get("ok", False) else HTTPStatus.BAD_REQUEST
            )
            self._send_json(result, status=status)
            return

        self._send_json(
            {"ok": False, "error": "Not found."},
            status=HTTPStatus.NOT_FOUND,
        )

    def _serve_static(self, path: str) -> bool:
        asset = _STATIC_ASSETS.get(path)
        if asset is None:
            return False
        data = _load_static_asset(asset["file"])
        if data is None:
            self._send_json(
                {"ok": False, "error": "Static asset missing."},
                status=HTTPStatus.NOT_FOUND,
            )
            return True
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", asset["content_type"])
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)
        return True

    def _read_json_payload(self) -> Optional[Mapping[str, Any]]:
        length_value = self.headers.get("Content-Length", "0")
        try:
            length = int(length_value)
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(
                {"ok": False, "error": "Invalid JSON."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return None

    def _send_json(
        self, payload: Mapping[str, Any], status: HTTPStatus = HTTPStatus.OK
    ) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def _optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_seed(value: Any) -> Optional[int] | bool:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return False


def _session_id_from_action_path(path: str) -> Optional[str]:
    parts = path.strip("/").split("/")
    if len(parts) == 4 and parts[:2] == ["api", "session"] and parts[3] == "action":
        return parts[2]
    return None


def _load_static_asset(filename: str) -> Optional[bytes]:
    try:
        return (_STATIC_ROOT / filename).read_bytes()
    except FileNotFoundError:
        return None


_STATIC_ROOT = resources.files("classic_cli_boardgames.web.static")
_STATIC_ASSETS = {
    "/": {"file": "index.html", "content_type": "text/html; charset=utf-8"},
    "/index.html": {"file": "index.html", "content_type": "text/html; charset=utf-8"},
    "/app.css": {"file": "app.css", "content_type": "text/css; charset=utf-8"},
    "/app.js": {"file": "app.js", "content_type": "text/javascript; charset=utf-8"},
}


def create_server(
    host: str = DEFAULT_HOST, port: int = DEFAULT_PORT
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), WebHandler)


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> int:
    server = create_server(host, port)
    host_display, port_display = server.server_address[:2]
    print(
        f"Classic CLI Boardgames web UI running at http://{host_display}:{port_display}"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the local Classic CLI Boardgames web UI.",
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    raise SystemExit(main())
