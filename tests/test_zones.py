from pathlib import Path

from graph import Graph
from routing import Router

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NETWORK_FILE = PROJECT_ROOT / "data" / "network.json"


def build_router():
    graph = Graph.from_json(NETWORK_FILE)
    return graph, Router(graph)


def test_zones_include_all_stations():
    graph, router = build_router()

    zones = router.zones()

    stations_in_zones = {
        station
        for zone in zones
        for station in zone
    }

    assert stations_in_zones == set(graph.stations.values())


def test_zones_do_not_duplicate_stations():
    _, router = build_router()

    zones = router.zones()

    stations = [
        station
        for zone in zones
        for station in zone
    ]

    assert len(stations) == len(set(stations))


def test_zones_are_not_empty():
    _, router = build_router()

    zones = router.zones()

    assert all(len(zone) > 0 for zone in zones)


def test_zone_count_is_at_least_one():
    _, router = build_router()

    zones = router.zones()

    assert len(zones) >= 1