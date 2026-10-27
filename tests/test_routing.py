"""Automated tests for the core routing behavior."""

from pathlib import Path

from graph import Graph
from routing import Router


PROJECT_ROOT = Path(__file__).resolve().parent.parent
NETWORK_FILE = PROJECT_ROOT / "data" / "network.json"


def build_router():
    """Create a fresh graph and router for each test."""
    graph = Graph.from_json(NETWORK_FILE)
    router = Router(graph)
    return graph, router


def test_known_route_exists():
    graph, router = build_router()

    result = router.shortest_time("Ameerpet", "Moosapet")

    assert result is not None
    assert result["minutes"] > 0
    assert result["stations"][0] == graph.find_station("Ameerpet")
    assert result["stations"][-1] == graph.find_station("Moosapet")


def test_same_station_route_has_zero_time():
    _, router = build_router()

    result = router.shortest_time("Ameerpet", "Ameerpet")

    assert result is not None
    assert result["minutes"] == 0
    assert len(result["stations"]) == 1


def test_unknown_station_returns_no_route():
    _, router = build_router()

    result = router.shortest_time("Fake Station", "Ameerpet")

    assert result is None


def test_route_has_one_line_per_segment():
    _, router = build_router()

    result = router.shortest_time("Ameerpet", "Moosapet")

    assert result is not None
    assert len(result["lines"]) == len(result["stations"]) - 1


def test_route_has_positive_distance():
    _, router = build_router()

    result = router.shortest_time("Ameerpet", "Moosapet")

    assert result is not None
    assert result["distance_km"] > 0


def test_route_between_different_stations_has_stops():
    _, router = build_router()

    result = router.shortest_time("Ameerpet", "Parade Grounds")

    assert result is not None
    assert len(result["stations"]) >= 2
    assert result["minutes"] > 0