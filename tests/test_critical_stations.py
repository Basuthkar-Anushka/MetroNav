
from critical_stations import find_critical_stations



def make_graph(edges):
    """Create a small graph for critical-station tests."""
    from types import SimpleNamespace

    station_ids = sorted({station for edge in edges for station in edge})

    graph = SimpleNamespace(
        stations={station_id: str(station_id) for station_id in station_ids},
        adjacency={station_id: [] for station_id in station_ids},
        closed_stations=set(),
        closed_segments=set(),
    )

    for first, second in edges:
        graph.adjacency[first].append({
            "destination": second,
            "minutes": 1,
            "km": 1,
            "line": "Test",
        })
        graph.adjacency[second].append({
            "destination": first,
            "minutes": 1,
            "km": 1,
            "line": "Test",
        })

    return graph


def test_middle_station_in_a_line_is_critical():
    graph = make_graph([(0, 1), (1, 2)])

    assert find_critical_stations(graph) == ["1"]


def test_triangle_has_no_critical_stations():
    graph = make_graph([(0, 1), (1, 2), (2, 0)])

    assert find_critical_stations(graph) == []


def test_two_branches_have_critical_center():
    graph = make_graph([(0, 1), (1, 2), (1, 3)])

    assert find_critical_stations(graph) == ["1"]


def test_closed_segment_changes_critical_stations():
    graph = make_graph([(0, 1), (1, 2), (2, 0)])
    graph.closed_segments.add(frozenset((0, 2)))

    assert find_critical_stations(graph) == ["1"]


def test_closed_station_is_not_reported():
    graph = make_graph([(0, 1), (1, 2)])
    graph.closed_stations.add(1)

    assert find_critical_stations(graph) == []
