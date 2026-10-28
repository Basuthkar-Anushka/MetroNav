
import argparse
import json
import csv
from pathlib import Path
from trie import Trie
from graph import Graph
from routing import Router
from fares import FareCalculator
from critical_stations import find_critical_stations
from busiest_stations import find_busiest_stations
from ticket_queue import TicketQueue
from expansion import find_expansion_tracks

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_FOLDER = PROJECT_ROOT / "data"

NETWORK_FILE = DATA_FOLDER / "network.json"
FARES_FILE = DATA_FOLDER / "fares.json"
RECENT_FILE = DATA_FOLDER / "recent_routes.json"
STATE_FILE = DATA_FOLDER / "network_state.json"
MAX_RECENT_ROUTES = 10


def load_recent_routes():
    """Load saved route history, newest first."""
    if not RECENT_FILE.exists():
        return []

    with RECENT_FILE.open("r", encoding="utf-8") as file:
        routes = json.load(file)

    if not isinstance(routes, list):
        raise ValueError("Recent routes file must contain a JSON list")

    return routes[:MAX_RECENT_ROUTES]


def save_recent_route(origin, destination, mode, result):
    """Save a successful route, keeping the newest first."""
    routes = load_recent_routes()

    # Remove an older entry for the same route and mode.
    routes = [
        route for route in routes
        if not (
            route["origin"] == origin
            and route["destination"] == destination
            and route["mode"] == mode
        )
    ]

    routes.insert(0, {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "minutes": result["minutes"],
        "stations": result["stations"],
        "lines": result["lines"],
        "distance_km": result["distance_km"],
        "interchanges": result["interchanges"],
    })

    RECENT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with RECENT_FILE.open("w", encoding="utf-8") as file:
        json.dump(routes[:MAX_RECENT_ROUTES], file, indent=2)


def load_network_state(graph):
    """Restore saved station and segment closures."""
    if not STATE_FILE.exists():
        return

    with STATE_FILE.open("r", encoding="utf-8") as file:
        state = json.load(file)

    for station_name in state.get("closed_stations", []):
        station_id = graph.find_station(station_name)
        if station_id is None:
            raise ValueError(
                f"Saved state contains unknown station: {station_name}"
            )
        graph.closed_stations.add(station_id)

    for pair in state.get("closed_segments", []):
        if len(pair) != 2:
            raise ValueError("Invalid closed segment in saved state")
        station_a, station_b = pair
        graph.close_segment(station_a, station_b)


def save_network_state(graph):
    """Persist current station and segment closures."""
    state = {
        "closed_stations": [
            graph.stations[station_id]
            for station_id in sorted(graph.closed_stations)
        ],
        "closed_segments": [
            sorted([
                graph.stations[station_id]
                for station_id in segment
            ])
            for segment in sorted(
                graph.closed_segments,
                key=lambda item: sorted(item)
            )
        ],
    }

    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)


def load_ticket_queue(journeys_file):
    """Load journey requests in file order into the priority queue."""
    queue = TicketQueue()

    with journeys_file.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        required = {"timestamp", "origin", "destination", "peak"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                "Journey file must contain timestamp, origin, "
                "destination, and peak columns"
            )

        for row in reader:
            origin = (row.get("origin") or "").strip()
            destination = (row.get("destination") or "").strip()
            timestamp = (row.get("timestamp") or "").strip()
            peak_text = (row.get("peak") or "").strip()

            if not origin or not destination or not timestamp:
                continue

            if peak_text not in {"0", "1"}:
                continue

            queue.enqueue({
                "timestamp": timestamp,
                "origin": origin,
                "destination": destination,
                "peak": int(peak_text),
            })

    return queue


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

    # Mode
    route_parser.add_argument(
        "--mode",
        choices=["fastest", "fewest-interchanges", "cheapest"],
        default="fastest",
        help="Routing preference"
    )

    # Recent Command
    subparsers.add_parser(
        "recent",
        help="Display recently cached routes"
    )

    # Critical stations command
    subparsers.add_parser(
        "critical",
        help="Find stations whose removal disconnects the network"
    )

    # Close Station Command
    close_parser = subparsers.add_parser(
        "close", help="Close a station"
    )
    close_parser.add_argument("station")

    # Open Station Command
    open_parser = subparsers.add_parser(
        "open", help="Reopen a station"
    )
    open_parser.add_argument("station")

    # Close Segment command
    close_segment_parser = subparsers.add_parser(
        "close-segment", help="Close a track segment"
    )
    close_segment_parser.add_argument("station_a")
    close_segment_parser.add_argument("station_b")

    # Re-open segment command
    reopen_segment_parser = subparsers.add_parser(
        "reopen-segment",
        help="Reopen a closed track segment"
    )
    reopen_segment_parser.add_argument("station_a")
    reopen_segment_parser.add_argument("station_b")

    # Zones command
    subparsers.add_parser(
        "zones",
        help="Display connected zones in the metro network"
    )

    # Network expansion command
    subparsers.add_parser(
        "expand",
        help="Find the cheapest candidate tracks to expand the network"
    )

    # Reach command
    reach_parser = subparsers.add_parser(
        "reach",
        help="Find stations reachable within a time limit"
    )
    reach_parser.add_argument("origin")
    reach_parser.add_argument(
        "--minutes",
        type=float,
        required=True,
        help="Maximum journey time in minutes"
    )

    top_parser = subparsers.add_parser(
        "top",
        help="Show the busiest stations"
    )
    top_parser.add_argument(
        "--k",
        type=int,
        required=True,
        help="Number of busiest stations to display"
    )

    queue_parser = subparsers.add_parser(
        "queue",
        help="Show the first N journeys in service order"
    )
    queue_parser.add_argument(
        "--n",
        type=int,
        required=True,
        help="Number of requests to display"
    )

    args = parser.parse_args()

    try:
        graph = Graph.from_json(NETWORK_FILE)
        load_network_state(graph)

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

        elif args.command == "recent":

            recent_routes = load_recent_routes()

            if not recent_routes:

                print("No recent routes saved yet.")

            else:

                print("Recent Routes (most recent first)")

                print("----------------------------------")

                for route in recent_routes:
                    print(

                        f"{route['origin']} -> {route['destination']} "

                        f"({route['mode']}): {route['minutes']} minutes"

                    )

        elif args.command == "critical":
            critical_stations = find_critical_stations(graph)

            print("Critical Stations")
            print("-----------------")

            if critical_stations:
                for station in critical_stations:
                    print("-", station)
            else:
                print("No critical stations found.")

        elif args.command == "close":
            graph.close_station(args.station)
            save_network_state(graph)
            print(f"Station closed: {args.station}")

        elif args.command == "open":
            graph.reopen_station(args.station)
            save_network_state(graph)
            print(f"Station reopened: {args.station}")

        elif args.command == "close-segment":
            graph.close_segment(args.station_a, args.station_b)
            save_network_state(graph)
            print(
                f"Track segment closed: "
                f"{args.station_a} <-> {args.station_b}")

        elif args.command == "reopen-segment":
            graph.reopen_segment(args.station_a, args.station_b)
            save_network_state(graph)
            print(
                f"Track segment reopened: "
                f"{args.station_a} <-> {args.station_b}")

        elif args.command == "expand":
            candidate_file = DATA_FOLDER / "candidate_tracks.json"

            selected_tracks, total_cost = find_expansion_tracks(
                graph,
                candidate_file
            )

            if not selected_tracks:
                print("No additional tracks are needed to connect the network.")
            else:
                print("Recommended Network Expansion")
                print("------------------------------")

                for track in selected_tracks:
                    print(
                        f"{track['id']}: "
                        f"{track['from']} -> {track['to']} | "
                        f"{track['cost_crore']} crore INR"
                    )

                print(f"Total construction cost: {total_cost:g} crore INR")

        elif args.command == "zones":
            router = Router(graph)

            zones = router.zones()

            print("Connected Zones")
            print("---------------")

            for index, zone in enumerate(zones, start=1):
                print(f"Zone {index}: {', '.join(sorted(zone))}")

            if not zones:
                print("No open stations found.")

        elif args.command == "reach":
            router = Router(graph)

            reachable = router.stations_within_time(
                args.origin,
                args.minutes
            )

            if not reachable:
                print("No stations reachable within the given time.")
            else:
                print(
                    f"Stations reachable from {args.origin} "
                    f"within {args.minutes:g} minutes:"
                )

                for station, minutes in sorted(
                    reachable.items(),
                    key=lambda item: (item[1], item[0].casefold())
                ):
                    print(f"- {station}: {minutes:g} minutes")

        elif args.command == "top":
            journeys_file = DATA_FOLDER / "journeys.txt"

            valid_stations = {
                name.casefold(): name
                for name in graph.stations.values()
            }

            busiest, invalid_rows = find_busiest_stations(
                journeys_file,
                args.k,
                valid_stations=valid_stations
            )

            if not busiest:
                print("No valid journey records found.")
            else:
                print(f"Top {len(busiest)} busiest stations:")
                for rank, (station, count) in enumerate(busiest, start=1):
                    label = "visit" if count == 1 else "visits"
                    print(f"{rank}. {station}: {count} {label}")

            print(f"Invalid journey rows skipped: {invalid_rows}")

        elif args.command == "queue":
            if args.n < 0:
                raise ValueError("N cannot be negative")

            journeys_file = DATA_FOLDER / "journeys.txt"
            ticket_queue = load_ticket_queue(journeys_file)
            requests = ticket_queue.first_n(args.n)

            if not requests:
                print("No valid journey requests to display.")
            else:
                print(f"First {len(requests)} requests in service order:")
                for index, request in enumerate(requests, start=1):
                    print(
                        f"{index}. {request['timestamp']} | "
                        f"{request['origin']} -> {request['destination']} | "
                        f"peak={request['peak']}"
                    )

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

            save_recent_route(
                args.origin,
                args.destination,
                args.mode,
                result
            )

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
