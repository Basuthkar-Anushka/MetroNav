"""Automated tests for the core routing behavior."""

from pathlib import Path

from graph import Graph
from routing import Router
from fares import FareCalculator

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


def test_fewest_interchanges_mode_returns_valid_route():
    graph, router = build_router()

    result = router.find_route(
        "Miyapur",
        "Nagole",
        mode="fewest-interchanges",
    )

    assert result is not None
    assert result["stations"][0] == graph.find_station("Miyapur")
    assert result["stations"][-1] == graph.find_station("Nagole")
    assert len(result["lines"]) == len(result["stations"]) - 1

    actual_changes = sum(
        result["lines"][i] != result["lines"][i - 1]
        for i in range(1, len(result["lines"]))
    )
    assert result["interchanges"] == actual_changes


def test_cheapest_mode_returns_a_valid_route():
    graph = Graph.from_json(NETWORK_FILE)
    fares_file = PROJECT_ROOT / "data" / "fares.json"
    fare_calculator = FareCalculator.from_json(fares_file)
    router = Router(graph, fare_calculator)

    result = router.find_route(
        "Miyapur",
        "Nagole",
        mode="cheapest",
    )

    assert result is not None
    assert result["stations"][0] == graph.find_station("Miyapur")
    assert result["stations"][-1] == graph.find_station("Nagole")
    assert len(result["lines"]) == len(result["stations"]) - 1
    assert result["distance_km"] >= 0
    assert result["minutes"] >= 0


def test_cheapest_mode_prefers_lower_fare_over_faster_route():
    network_data = {
        "interchange_penalty_minutes": 0,
        "stations": [
            {"id": "A", "name": "Station A"},
            {"id": "B", "name": "Station B"},
            {"id": "C", "name": "Station C"},
            {"id": "D", "name": "Station D"},
        ],
        "connections": [
            {
                "from": "A", "to": "B",
                "line": "Red", "minutes": 5, "km": 1,
            },
            {
                "from": "B", "to": "D",
                "line": "Red", "minutes": 5, "km": 1,
            },
            {
                "from": "A", "to": "C",
                "line": "Blue", "minutes": 2, "km": 2.5,
            },
            {
                "from": "C", "to": "D",
                "line": "Blue", "minutes": 2, "km": 2.5,
            },
        ],
    }

    graph = Graph(network_data)
    fares_file = PROJECT_ROOT / "data" / "fares.json"
    fare_calculator = FareCalculator.from_json(fares_file)
    router = Router(graph, fare_calculator)

    result = router.find_route(
        "Station A",
        "Station D",
        mode="cheapest",
    )

    assert result is not None
    assert result["stations"] == ["A", "B", "D"]
    assert result["distance_km"] == 2
    assert result["minutes"] == 10


def test_cheapest_mode_breaks_equal_fare_tie_by_time():
    network_data = {
        "interchange_penalty_minutes": 0,
        "stations": [
            {"id": "A", "name": "Station A"},
            {"id": "B", "name": "Station B"},
            {"id": "C", "name": "Station C"},
            {"id": "D", "name": "Station D"},
        ],
        "connections": [
            {
                "from": "A", "to": "B",
                "line": "Red", "minutes": 8, "km": 0.5,
            },
            {
                "from": "B", "to": "D",
                "line": "Red", "minutes": 8, "km": 0.5,
            },
            {
                "from": "A", "to": "C",
                "line": "Blue", "minutes": 2, "km": 0.5,
            },
            {
                "from": "C", "to": "D",
                "line": "Blue", "minutes": 2, "km": 0.5,
            },
        ],
    }

    graph = Graph(network_data)
    fares_file = PROJECT_ROOT / "data" / "fares.json"
    fare_calculator = FareCalculator.from_json(fares_file)
    router = Router(graph, fare_calculator)

    result = router.find_route(
        "Station A",
        "Station D",
        mode="cheapest",
    )

    assert result is not None
    assert result["stations"] == ["A", "C", "D"]
    assert result["distance_km"] == 1
    assert result["minutes"] == 4
    assert fare_calculator.calculate_fare(result["distance_km"]) == 10


def test_fewest_interchanges_prefers_fewer_changes_over_shorter_time():
    network_data = {
        "interchange_penalty_minutes": 0,
        "stations": [
            {"id": "A", "name": "Station A"},
            {"id": "B", "name": "Station B"},
            {"id": "C", "name": "Station C"},
            {"id": "D", "name": "Station D"},
        ],
        "connections": [
            # Faster route: two line changes.
            {
                "from": "A", "to": "B",
                "line": "Red", "minutes": 1, "km": 1,
            },
            {
                "from": "B", "to": "D",
                "line": "Blue", "minutes": 1, "km": 1,
            },
            # Slower route: no line changes.
            {
                "from": "A", "to": "C",
                "line": "Green", "minutes": 5, "km": 1,
            },
            {
                "from": "C", "to": "D",
                "line": "Green", "minutes": 5, "km": 1,
            },
        ],
    }

    graph = Graph(network_data)
    router = Router(graph)

    result = router.find_route(
        "Station A",
        "Station D",
        mode="fewest-interchanges",
    )

    assert result is not None
    assert result["stations"] == ["A", "C", "D"]
    assert result["interchanges"] == 0
    assert result["minutes"] == 10
