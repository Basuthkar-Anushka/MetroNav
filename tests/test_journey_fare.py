
from pathlib import Path
from graph import Graph
from routing import Router
from fares import FareCalculator

PROJECT_ROOT = Path(__file__).resolve().parent.parent

graph = Graph.from_json(
    PROJECT_ROOT / "data" / "network.json"
)

fare_calculator = FareCalculator.from_json(
    PROJECT_ROOT / "data" / "fares.json"
)

router = Router(graph)

result = router.shortest_time("Ameerpet", "Moosapet")

assert result is not None

distance = result["distance_km"]
fare = fare_calculator.calculate_fare(distance)

print("Journey: Ameerpet -> Moosapet")
print("Distance:", distance, "km")
print("Travel time:", result["minutes"], "minutes")
print("Fare: Rs.", fare)

assert fare == 40

print("Journey fare integration test passed!")
