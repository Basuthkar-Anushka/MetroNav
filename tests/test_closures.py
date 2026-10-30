
from pathlib import Path
import pytest
from graph import Graph
from routing import Router


PROJECT_ROOT = Path(__file__).resolve().parent.parent
NETWORK_FILE = PROJECT_ROOT / "data" / "network.json"


def build_router():
    graph = Graph.from_json(NETWORK_FILE)
    return graph, Router(graph)


def test_closing_and_reopening_station():
    graph, router = build_router()

    router.close_station("Ameerpet")
    assert graph.find_station("Ameerpet") in graph.closed_stations

    router.reopen_station("Ameerpet")
    assert graph.find_station("Ameerpet") not in graph.closed_stations


def test_closing_and_reopening_segment():
    graph, router = build_router()

    # Find a real connection in the network.
    source_id = graph.find_station("Ameerpet")
    edge = graph.adjacency[source_id][0]
    destination_id = edge["destination"]

    source_name = graph.stations[source_id]
    destination_name = graph.stations[destination_id]

    router.close_segment(source_name, destination_name)

    segment = frozenset((source_id, destination_id))
    assert segment in graph.closed_segments

    router.reopen_segment(source_name, destination_name)
    assert segment not in graph.closed_segments


def test_closed_station_is_not_a_routing_neighbor():
    graph, router = build_router()

    station_id = graph.find_station("Ameerpet")
    router.close_station("Ameerpet")

    assert router.get_neighbors(station_id) == []


def test_closing_station_clears_route_cache():
    graph, router = build_router()

    origin_id = graph.find_station("Ameerpet")
    destination_id = graph.find_station("Moosapet")
    cache_key = (origin_id, destination_id, "fastest")

    # Add a known entry to the cache.
    router.route_cache.put(cache_key, "test route")
    assert router.route_cache.get(cache_key) == "test route"

    # Closing a station should clear the entire route cache.
    router.close_station("Ameerpet")

    assert router.route_cache.get(cache_key) is None


def test_closed_segment_is_not_a_routing_neighbor():
    graph, router = build_router()

    source_id = graph.find_station("Ameerpet")
    edge = graph.adjacency[source_id][0]
    destination_id = edge["destination"]

    destination_name = graph.stations[destination_id]

    # Confirm the connection exists before closing it.
    assert any(
        neighbor["destination"] == destination_id
        for neighbor in router.get_neighbors(source_id)
    )

    router.close_segment("Ameerpet", destination_name)

    # The closed connection should no longer be available.
    assert not any(
        neighbor["destination"] == destination_id
        for neighbor in router.get_neighbors(source_id)
    )


def test_stations_within_time_includes_origin():
    _, router = build_router()

    result = router.stations_within_time("Ameerpet", 15)

    assert result["Ameerpet"] == 0
    assert all(minutes <= 15 for minutes in result.values())


def test_stations_within_time_counts_interchange_penalty():
    _, router = build_router()

    result = router.stations_within_time("Miyapur", 28)

    assert result["Ameerpet"] == 26
    assert "Nagole" not in result


def test_stations_beyond_time_limit_are_excluded():
    _, router = build_router()

    result = router.stations_within_time("Ameerpet", 0)

    assert result == {"Ameerpet": 0}


def test_closed_station_is_excluded_from_reachability():
    graph, router = build_router()

    source_id = graph.find_station("Ameerpet")
    edge = graph.adjacency[source_id][0]
    closed_station_name = graph.stations[edge["destination"]]

    router.close_station(closed_station_name)

    result = router.stations_within_time("Ameerpet", 60)

    assert closed_station_name not in result


def test_closing_already_closed_station_raises_error():
    graph, router = build_router()
    router.close_station("Ameerpet")

    with pytest.raises(ValueError, match="already closed"):
        router.close_station("Ameerpet")


def test_reopening_segment_that_is_not_closed_raises_error():
    graph, router = build_router()

    station_a = "Ameerpet"
    station_a_id = graph.find_station(station_a)

    station_b_id = next(
        edge["destination"]
        for edge in graph.adjacency[station_a_id]
    )
    station_b = graph.stations[station_b_id]

    with pytest.raises(ValueError, match="Segment is not closed"):
        graph.reopen_segment(station_a, station_b)


def test_reopening_station_that_is_not_closed_raises_error():
    graph, router = build_router()

    with pytest.raises(ValueError, match="not closed"):
        router.reopen_station("Ameerpet")


def test_closing_unknown_station_raises_error():
    _, router = build_router()

    with pytest.raises(ValueError, match="Unknown station"):
        router.close_station("NotARealStation")


def test_reopening_unknown_station_raises_error():
    _, router = build_router()

    with pytest.raises(ValueError, match="Unknown station"):
        router.reopen_station("NotARealStation")


def test_closing_nonexistent_segment_raises_error():
    _, router = build_router()

    with pytest.raises(ValueError, match="No track segment"):
        router.close_segment("Ameerpet", "LB Nagar")


def test_reopening_nonexistent_segment_raises_error():
    _, router = build_router()

    with pytest.raises(ValueError, match="No track segment"):
        router.reopen_segment("Ameerpet", "LB Nagar")


def test_closing_segment_with_unknown_station_raises_error():
    _, router = build_router()

    with pytest.raises(ValueError, match="Unknown station"):
        router.close_segment("Ameerpet", "NotARealStation")
