
import json
from pathlib import Path

from union_find import UnionFind
from min_heap import MinHeap


def find_expansion_tracks(graph, candidate_file):
    """Choose the cheapest candidate tracks using Kruskal's algorithm."""
    candidate_file = Path(candidate_file)

    try:
        with candidate_file.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid candidate tracks JSON: {error.msg}"
        ) from error
    except OSError as error:
        raise ValueError(
            f"Cannot read candidate tracks file: {error}"
        ) from error

    if not isinstance(data, dict) or not isinstance(data.get("tracks"), list):
        raise ValueError("Candidate file must contain a 'tracks' list")

    station_ids = list(graph.stations)
    union_find = UnionFind(station_ids)

    # Register existing connections first, so we only select
    # candidate tracks that connect separate components.
    for station_id, edges in graph.adjacency.items():
        for edge in edges:
            union_find.union(station_id, edge["destination"])

    # A min-heap orders tracks by cost, then ID for deterministic ties.
    heap = MinHeap()
    for track in data["tracks"]:
        if not isinstance(track, dict):
            raise ValueError("Each candidate track must be an object")

        required = {"id", "from", "to", "cost_crore"}
        if not required.issubset(track):
            raise ValueError(
                "Each candidate track needs id, from, to, and cost_crore"
            )

        source = track["from"]
        destination = track["to"]
        cost = track["cost_crore"]

        if source not in graph.stations or destination not in graph.stations:
            raise ValueError(
                f"Track {track['id']} references an unknown station"
            )

        if (
            not isinstance(cost, (int, float))
            or isinstance(cost, bool)
            or cost < 0
        ):
            raise ValueError(
                f"Track {track['id']} has an invalid construction cost"
            )

        heap.push((cost, str(track["id"]), track))

    selected = []
    total_cost = 0


    while not heap.is_empty():
        cost, _, track = heap.pop()

        if union_find.union(track["from"], track["to"]):
            selected.append(track)
            total_cost += cost

    # All stations must belong to one connected component.
    if station_ids:
        first_station = station_ids[0]
        if any(
            union_find.find(station_id) != union_find.find(first_station)
            for station_id in station_ids[1:]
        ):
            raise ValueError(
                "The candidate tracks cannot connect every station "
                "into one network."
            )

    return selected, total_cost
