from pathlib import Path

from graph import Graph
from routing import Router


# Load the metro network.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
NETWORK_FILE = PROJECT_ROOT / "data" / "network.json"

graph = Graph.from_json(NETWORK_FILE)
router = Router(graph)


def test_interchange_penalty():
    # Find a route that uses more than one line.
    result = router.shortest_time("Miyapur", "Nagole")

    assert result is not None

    # Count how many times the line changes.
    lines = result["lines"]
    changes = sum(
        lines[i] != lines[i - 1]
        for i in range(1, len(lines))
    )

    print("Route lines:", lines)
    print("Number of line changes:", changes)
    print("Total travel time:", result["minutes"], "minutes")

    assert changes == 1

    # Calculate the journey time independently.
    expected_minutes = 0

    for i in range(len(result["stations"]) - 1):
        current_station = result["stations"][i]
        next_station = result["stations"][i + 1]
        line = result["lines"][i]

        # Find the connection between these two stations on this line.
        for edge in graph.adjacency[current_station]:
            if (
                    edge["destination"] == next_station
                    and edge["line"] == line
            ):
                expected_minutes += edge["minutes"]
                break

    # Add the interchange penalty for each line change.
    expected_minutes += changes * graph.interchange_penalty

    print("Router time:", result["minutes"])
    print("Independently calculated time:", expected_minutes)

    assert result["minutes"] == expected_minutes

    print("Interchange penalty test passed!")


if __name__ == "__main__":
    test_interchange_penalty()
