from pathlib import Path

from graph import Graph
from routing import Router

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NETWORK_FILE = PROJECT_ROOT / "data" / "network.json"

graph = Graph.from_json(NETWORK_FILE)
router = Router(graph)

result = router.shortest_time("Ameerpet", "Moosapet")

print(result)

assert result is not None
assert result["minutes"] > 0
assert result["stations"][0] == graph.find_station("Ameerpet")
assert result["stations"][-1] == graph.find_station("Moosapet")

print("Basic routing test passed!")

if result is not None:
    station_names = [
        graph.stations[station_id]
        for station_id in result["stations"]
    ]

    print("Route:", " -> ".join(station_names))
    print("Total time:", result["minutes"], "minutes")

    # Check that a route between two valid stations is found.
    result = router.shortest_time("Ameerpet", "Moosapet")

    assert result is not None
    assert result["minutes"] > 0

    print("Basic routing test passed!")

    # Check the zero-distance journey.
    same_station = router.shortest_time("Ameerpet", "Ameerpet")

    assert same_station is not None
    assert same_station["minutes"] == 0
    assert len(same_station["stations"]) == 1

    print("Same-station test passed!")


# Show the route and the line used for each segment.
result = router.shortest_time("Ameerpet", "Moosapet")

if result is not None:
    station_names = [
        graph.stations[station_id]
        for station_id in result["stations"]
    ]

    print("Route:", " -> ".join(station_names))
    print("Lines:", result["lines"])
    print("Total time:", result["minutes"], "minutes")


print("\nTesting a route that may change lines:")

result = router.shortest_time("Ameerpet", "Parade Grounds")

if result is not None:
    station_names = [
        graph.stations[station_id]
        for station_id in result["stations"]
    ]

    print("Route:", " -> ".join(station_names))
    print("Lines:", result["lines"])
    print("Total time:", result["minutes"], "minutes")
else:
    print("No route found.")


# Find a route that uses more than one metro line

for origin_name in graph.name_to_id:
    for destination_name in graph.name_to_id:
        if origin_name == destination_name:
            continue

        result = router.shortest_time(
            origin_name,
            destination_name
        )

        if result is not None and len(set(result["lines"])) > 1:
            print("\nFound a route with a line change!")
            print("From:", origin_name)
            print("To:", destination_name)
            print("Lines:", result["lines"])
            print("Minutes:", result["minutes"])
            raise SystemExit

# Unknown station test
unknown = router.shortest_time("Fake Station", "Ameerpet")
assert unknown is None

print("Unknown-station test passed!")

result = router.shortest_time("Ameerpet", "Moosapet")

assert result is not None
assert result["distance_km"] > 0

print("Journey distance:", result["distance_km"], "km")
print("Journey time:", result["minutes"], "minutes")
print("Distance test passed!")