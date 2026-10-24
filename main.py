
import argparse
from pathlib import Path
from trie import Trie
from graph import Graph
from routing import Router
from fares import FareCalculator


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FOLDER = PROJECT_ROOT / "data"

NETWORK_FILE = DATA_FOLDER / "network.json"
FARES_FILE = DATA_FOLDER / "fares.json"


def main():
    parser = argparse.ArgumentParser(
        description="MetroNav - Metro Network Navigator"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # Info command
    subparsers.add_parser(
        "info",
        help="Display network information"
    )

    # Station suggestion command
    suggest_parser = subparsers.add_parser(
        "suggest",
        help="Suggest stations matching a prefix"
    )
    suggest_parser.add_argument("prefix")

    # Route command
    route_parser = subparsers.add_parser(
        "route",
        help="Find a route between two stations"
    )
    route_parser.add_argument("origin")
    route_parser.add_argument("destination")

    route_parser.add_argument(
        "--mode",
        choices=["fastest", "fewest-interchanges", "cheapest"],
        default="fastest",
        help="Routing preference"
    )

    args = parser.parse_args()

    try:
        graph = Graph.from_json(NETWORK_FILE)

        if args.command == "info":
            print("MetroNav Network Information")
            print("----------------------------")
            print("Stations:", len(graph.stations))
            print(
                "Connections:",
                sum(
                    len(edges)
                    for edges in graph.adjacency.values()
                ) // 2
            )

        elif args.command == "suggest":
            trie = Trie()

            for station_name in graph.stations.values():
                trie.insert(station_name)

            suggestions = trie.search_prefix(args.prefix)

            if suggestions:
                print("Station suggestions:")
                for station in suggestions:
                    print("-", station)
            else:
                print("No stations found for that prefix.")

        elif args.command == "route":
            fare_calculator = FareCalculator.from_json(FARES_FILE)
            router = Router(graph, fare_calculator)

            result = router.find_route(
                args.origin,
                args.destination,
                args.mode
            )

            if result is None:
                print(
                    "No route found. Check the station names "
                    "or network connections."
                )
                return

            station_names = [
                graph.stations[station_id]
                for station_id in result["stations"]
            ]

            lines = result["lines"]
            fare = fare_calculator.calculate_fare(
                result["distance_km"]
            )

            print(f"Route: {' -> '.join(station_names)}")
            print(f"Mode: {args.mode}")
            print("Journey details:")

            if not lines:
                print("You are already at your destination.")
            else:
                print(f"[{lines[0]}] {station_names[0]}", end="")

                for i, line in enumerate(lines):
                    print(f" -> {station_names[i + 1]}", end="")

                    if i == len(lines) - 1:
                        print()
                    elif lines[i + 1] != line:
                        print()
                        print(
                            f"Change at {station_names[i + 1]}: "
                            f"{line} -> {lines[i + 1]} "
                            f"(+{graph.interchange_penalty} min)"
                        )
                        print(
                            f"[{lines[i + 1]}] "
                            f"{station_names[i + 1]}",
                            end=""
                        )

            print("Stops:", len(station_names) - 1)
            print("Interchanges:", result["interchanges"])
            print("Time:", result["minutes"], "min")
            print(
                "Distance:",
                round(result["distance_km"], 2),
                "km"
            )
            print("Fare: Rs", fare)

    except (OSError, ValueError, KeyError) as error:
        print("Unable to complete the command:", error)


if __name__ == "__main__":
    main()
