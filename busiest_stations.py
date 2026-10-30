
import csv
from collections import Counter
from pathlib import Path

from min_heap import MinHeap


def _reverse_name(name):
    """Create a sortable key that reverses alphabetical order."""
    return tuple(-ord(char) for char in name.casefold())


def find_busiest_stations(journeys_file, k, valid_stations=None):
    """Return the K busiest stations and the number of invalid journey rows."""
    if k < 0:
        raise ValueError("K cannot be negative")

    if k == 0:
        return [], 0

    visits = Counter()
    invalid_rows = 0

    with Path(journeys_file).open(
        "r", encoding="utf-8", newline=""
    ) as file:
        reader = csv.DictReader(file)

        required = {"timestamp", "origin", "destination", "peak"}
        if not reader.fieldnames or not required.issubset(
            set(reader.fieldnames)
        ):
            raise ValueError(
                "Journey file must contain timestamp, origin, "
                "destination, and peak columns"
            )

        for row in reader:
            origin = (row.get("origin") or "").strip()
            destination = (row.get("destination") or "").strip()
            timestamp = (row.get("timestamp") or "").strip()
            peak = (row.get("peak") or "").strip()

            if (
                not origin
                or not destination
                or not timestamp
                or peak not in {"0", "1"}
            ):
                invalid_rows += 1
                continue

            if valid_stations is not None:
                origin_key = origin.casefold()
                destination_key = destination.casefold()

                if (
                        origin_key not in valid_stations
                        or destination_key not in valid_stations
                ):
                    invalid_rows += 1
                    continue

                origin = valid_stations[origin_key]
                destination = valid_stations[destination_key]
            visits[origin] += 1
            visits[destination] += 1

    heap = MinHeap()

    for station, count in visits.items():
        # Keep the K busiest stations.
        # For equal counts, prefer alphabetical order.
        heap.push((count, _reverse_name(station), station))

        if len(heap.items) > k:
            heap.pop()

    busiest = []
    while not heap.is_empty():
        count, _, station = heap.pop()
        busiest.append((station, count))

    busiest.sort(key=lambda item: (-item[1], item[0].casefold()))

    return busiest, invalid_rows
