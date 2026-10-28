
import json

from expansion import find_expansion_tracks
from graph import Graph


def make_graph():
    """Create a small network with two disconnected components."""
    network_data = {
        "interchange_penalty_minutes": 5,
        "stations": [
            {"id": "A", "name": "Station A"},
            {"id": "B", "name": "Station B"},
            {"id": "C", "name": "Station C"},
            {"id": "D", "name": "Station D"},
        ],
        "connections": [
            {
                "from": "A",
                "to": "B",
                "line": "Red",
                "minutes": 3,
                "km": 2,
            },
            {
                "from": "C",
                "to": "D",
                "line": "Blue",
                "minutes": 4,
                "km": 3,
            },
        ],
    }
    return Graph(network_data)


def test_expansion_selects_cheapest_track():
    graph = make_graph()
    candidates = [
        {"id": "T1", "from": "A", "to": "C", "cost_crore": 100},
        {"id": "T2", "from": "B", "to": "D", "cost_crore": 40},
    ]

    # Use a temporary JSON file for candidate tracks.
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        candidate_file = Path(temp_dir) / "candidate_tracks.json"
        candidate_file.write_text(
            json.dumps({"tracks": candidates}),
            encoding="utf-8",
        )

        selected, total_cost = find_expansion_tracks(
            graph, candidate_file
        )

    assert [track["id"] for track in selected] == ["T2"]
    assert total_cost == 40


def test_expansion_does_not_add_track_inside_existing_component():
    graph = make_graph()
    candidates = [
        {"id": "T1", "from": "A", "to": "B", "cost_crore": 10},
        {"id": "T2", "from": "A", "to": "C", "cost_crore": 20},
    ]

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        candidate_file = Path(temp_dir) / "candidate_tracks.json"
        candidate_file.write_text(
            json.dumps({"tracks": candidates}),
            encoding="utf-8",
        )

        selected, total_cost = find_expansion_tracks(
            graph, candidate_file
        )

    assert [track["id"] for track in selected] == ["T2"]
    assert total_cost == 20


def test_expansion_rejects_unknown_station():
    graph = make_graph()
    candidates = [
        {"id": "T1", "from": "A", "to": "UNKNOWN", "cost_crore": 20},
    ]

    import tempfile
    from pathlib import Path
    import pytest

    with tempfile.TemporaryDirectory() as temp_dir:
        candidate_file = Path(temp_dir) / "candidate_tracks.json"
        candidate_file.write_text(
            json.dumps({"tracks": candidates}),
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="unknown station"):
            find_expansion_tracks(graph, candidate_file)

def test_expansion_reports_when_network_cannot_be_connected():
    import json
    import tempfile
    from pathlib import Path

    import pytest

    graph = make_graph()
    candidates = [
        {
            "id": "T1",
            "from": "A",
            "to": "B",
            "cost_crore": 10,
        }
    ]

    with tempfile.TemporaryDirectory() as temp_dir:
        candidate_file = Path(temp_dir) / "candidate_tracks.json"
        candidate_file.write_text(
            json.dumps({"tracks": candidates}),
            encoding="utf-8",
        )

        with pytest.raises(
            ValueError,
            match="cannot connect every station",
        ):
            find_expansion_tracks(graph, candidate_file)
