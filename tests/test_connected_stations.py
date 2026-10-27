from pathlib import Path

from graph import Graph


def build_graph():
    data_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "network.json"
    )
    return Graph.from_json(data_path)


def test_connected_stations_includes_origin():
    graph = build_graph()

    result = graph.connected_stations("Ameerpet")

    assert "Ameerpet" in result


def test_unknown_station_raises_error():
    graph = build_graph()

    try:
        graph.connected_stations("Not A Real Station")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for unknown station")


def test_closed_station_is_excluded():
    graph = build_graph()
    graph.close_station("Ameerpet")

    result = graph.connected_stations("Secunderabad East")

    assert "Ameerpet" not in result