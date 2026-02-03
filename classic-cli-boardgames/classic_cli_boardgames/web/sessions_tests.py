from classic_cli_boardgames.web.sessions import SessionStore, build_options_payload


def test_build_options_payload_defaults() -> None:
    payload = build_options_payload()
    assert "games" in payload
    assert "difficulties" in payload
    assert "player_modes" in payload
    assert payload["defaults"]["game"] == "chess"
    assert payload["defaults"]["difficulty"]
    assert payload["defaults"]["player_mode"]
    assert "chess" in payload["help"]
    game_keys = {game["key"] for game in payload["games"]}
    assert "go" in game_keys
    assert "go" in payload["help"]


def test_session_flow_help_and_move() -> None:
    store = SessionStore()
    session = store.create_session("chess")
    session_id = session["id"]

    help_response = store.handle_action(session_id, {"type": "help"})
    assert help_response["ok"] is True
    assert isinstance(help_response["help"], str)
    assert "help" in help_response["help"].lower()

    move_response = store.handle_action(session_id, {"type": "move", "text": "e2e4"})
    assert move_response["ok"] is True
    assert "played" in move_response["message"].lower()
    assert move_response["session"]["game_key"] == "chess"
