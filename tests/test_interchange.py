
from pathlib import Path

from graph import Graph
from routing import Router


PROJECT_ROOT = Path(__file__).resolve().parent.parent
NETWORK_FILE = PROJECT_ROOT / "data" / "network.json"


def test_interchange_penalty():
    graph = Graph.from_json(NETWORK_FILE)
    router = Router(graph)

    result = router.shortest_time("Miyapur", "Nagole")

    assert result is not None

    lines = result["lines"]
    changes = sum(
        lines[i] != lines[i - 1]
        for i in range(1, len(lines))
    )

    assert changes == 1

    expected_minutes = 0

    for i in range(len(result["stations"]) - 1):
        current_station = result["stations"][i]
        next_station = result["stations"][i + 1]
        line = result["lines"][i]

        matching_edge = next(
            (
                edge
                for edge in graph.adjacency[current_station]
                if (
                    edge["destination"] == next_station
                    and edge["line"] == line
                )
            ),
            None,
        )

        assert matching_edge is not None
        expected_minutes += matching_edge["minutes"]

    expected_minutes += changes * graph.interchange_penalty

    assert result["minutes"] == expected_minutes
