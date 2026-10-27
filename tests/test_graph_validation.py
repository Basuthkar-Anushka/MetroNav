
import pytest

from graph import Graph


def valid_network_data():
    return {
        "interchange_penalty_minutes": 5,
        "stations": [
            {"id": "A", "name": "Station A"},
            {"id": "B", "name": "Station B"},
        ],
        "connections": [
            {
                "from": "A",
                "to": "B",
                "line": "Red",
                "minutes": 4,
                "km": 2.5,
            }
        ],
    }


def test_missing_top_level_field_is_rejected():
    data = valid_network_data()
    del data["connections"]

    with pytest.raises(ValueError, match="missing fields"):
        Graph(data)


def test_missing_connection_field_is_rejected():
    data = valid_network_data()
    del data["connections"][0]["km"]

    with pytest.raises(ValueError, match="missing fields"):
        Graph(data)


def test_unknown_station_id_is_rejected():
    data = valid_network_data()
    data["connections"][0]["to"] = "UNKNOWN"

    with pytest.raises(ValueError, match="unknown station ID"):
        Graph(data)


def test_malformed_json_file_raises_clear_error(tmp_path):
    bad_file = tmp_path / "broken_network.json"
    bad_file.write_text(
        '{"stations": [}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid JSON"):
        Graph.from_json(bad_file)
