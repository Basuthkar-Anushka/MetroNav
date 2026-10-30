import json
from pathlib import Path
from union_find import UnionFind


class Graph:

    @staticmethod
    def _validate_network_data(network_data):
        """Validate network data before building the graph."""

        if not isinstance(network_data, dict):
            raise ValueError("Invalid network data: expected a JSON object")

        required_fields = {
            "stations",
            "connections",
            "interchange_penalty_minutes",
        }

        missing = required_fields - network_data.keys()
        if missing:
            raise ValueError(
                f"Invalid network data: missing fields: {sorted(missing)}"
            )

        if not isinstance(network_data["stations"], list):
            raise ValueError("'stations' must be a list")

        if not isinstance(network_data["connections"], list):
            raise ValueError("'connections' must be a list")

        penalty = network_data["interchange_penalty_minutes"]
        if (
            isinstance(penalty, bool)
            or not isinstance(penalty, (int, float))
            or penalty < 0
        ):
            raise ValueError(
                "'interchange_penalty_minutes' must be a non-negative number"
            )

        station_ids = set()
        station_names = set()

        # Validate stations first.
        for index, station in enumerate(network_data["stations"]):
            if not isinstance(station, dict):
                raise ValueError(f"Station at index {index} must be an object")

            for field in ("id", "name"):
                if field not in station:
                    raise ValueError(
                        f"Station at index {index} is missing field '{field}'"
                    )

            station_id = station["id"]
            name = station["name"]

            if not isinstance(station_id, str) or not station_id.strip():
                raise ValueError(
                    f"Station at index {index} has an invalid ID"
                )

            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    f"Station '{station_id}' has an invalid name"
                )

            if station_id in station_ids:
                raise ValueError(f"Duplicate station ID: {station_id}")

            if name.casefold() in station_names:
                raise ValueError(f"Duplicate station name: {name}")

            station_ids.add(station_id)
            station_names.add(name.casefold())

        # Validate connections and their station references.
        required_connection_fields = {
            "from", "to", "line", "minutes", "km"
        }

        for index, connection in enumerate(network_data["connections"]):
            if not isinstance(connection, dict):
                raise ValueError(
                    f"Connection at index {index} must be an object"
                )

            missing = required_connection_fields - connection.keys()
            if missing:
                raise ValueError(
                    f"Connection at index {index} is missing fields: "
                    f"{sorted(missing)}"
                )

            source = connection["from"]
            destination = connection["to"]
            line = connection["line"]

            if source not in station_ids:
                raise ValueError(
                    f"Connection at index {index} references unknown "
                    f"station ID: {source}"
                )

            if destination not in station_ids:
                raise ValueError(
                    f"Connection at index {index} references unknown "
                    f"station ID: {destination}"
                )

            if source == destination:
                raise ValueError(
                    f"Connection at index {index} connects a station to itself"
                )

            if not isinstance(line, str) or not line.strip():
                raise ValueError(
                    f"Connection at index {index} has an invalid line"
                )

            for field in ("minutes", "km"):
                value = connection[field]

                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or value < 0
                ):
                    raise ValueError(
                        f"Connection at index {index}: "
                        f"'{field}' must be a non-negative number"
                    )

    def __init__(self, network_data):
        self._validate_network_data(network_data)
        # Time added when a passenger changes metro lines.
        self.interchange_penalty = network_data[
            "interchange_penalty_minutes"
        ]

        # Station ID -> station name.
        self.stations: dict[str, str] = {}

        # Normalized station name -> station ID.
        self.name_to_id = {}

        # Station ID -> list of neighbouring connections.
        self.adjacency = {}

        # Track temporary closures without deleting network data.
        self.closed_stations = set()
        self.closed_segments = set()

        # First, register every station.
        for station in network_data["stations"]:
            station_id = station["id"]
            name = station["name"]

            self.stations[station_id] = name
            self.name_to_id[name.casefold()] = station_id
            self.adjacency[station_id] = []

        # Next, add every connection in both directions.
        for connection in network_data["connections"]:
            source = connection["from"]
            destination = connection["to"]

            edge = {
                "destination": destination,
                "line": connection["line"],
                "minutes": connection["minutes"],
                "km": connection["km"],
            }

            reverse_edge = {
                "destination": source,
                "line": connection["line"],
                "minutes": connection["minutes"],
                "km": connection["km"],
            }

            self.adjacency[source].append(edge)
            self.adjacency[destination].append(reverse_edge)

    @classmethod
    def from_json(cls, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                network_data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON in '{file_path}': {error.msg} "
                f"(line {error.lineno}, column {error.colno})"
            ) from error
        except OSError as error:
            raise ValueError(
                f"Cannot read network file '{file_path}': {error}"
            ) from error
        return cls(network_data)

    def find_station(self, name):
        normalized_name = name.strip().casefold()
        return self.name_to_id.get(normalized_name)

    def close_station(self, station_name):
        station_id = self.find_station(station_name)

        if station_id is None:
            raise ValueError(f"Unknown station: {station_name}")

        if station_id in self.closed_stations:
            raise ValueError(f"Station is already closed: {station_name}")

        self.closed_stations.add(station_id)

    def reopen_station(self, station_name):
        station_id = self.find_station(station_name)

        if station_id is None:
            raise ValueError(f"Unknown station: {station_name}")

        if station_id not in self.closed_stations:
            raise ValueError(f"Station is not closed: {station_name}")

        self.closed_stations.remove(station_id)

    def close_segment(self, station_a, station_b):
        id_a = self.find_station(station_a)
        id_b = self.find_station(station_b)

        if id_a is None or id_b is None:
            raise ValueError("Unknown station in segment")

        if not any(
            edge["destination"] == id_b
            for edge in self.adjacency[id_a]
        ):
            raise ValueError("No track segment connects these stations")

        self.closed_segments.add(frozenset((id_a, id_b)))

    def reopen_segment(self, station_a, station_b):
        id_a = self.find_station(station_a)
        id_b = self.find_station(station_b)

        if id_a is None or id_b is None:
            raise ValueError("Unknown station in segment")

        if not any(
                edge["destination"] == id_b
                for edge in self.adjacency[id_a]
        ):
            raise ValueError("No track segment connects these stations")

        segment = frozenset((id_a, id_b))

        if segment not in self.closed_segments:
            raise ValueError("Segment is not closed")

        self.closed_segments.remove(segment)

    def connected_stations(self, station_name):
        """Return all stations connected to the given station."""

        station_id = self.find_station(station_name)

        if station_id is None:
            raise ValueError(f"Unknown station: {station_name}")

        groups = UnionFind(self.stations.keys())

        # Join stations connected by open track segments.
        for source_id, edges in self.adjacency.items():
            if source_id in self.closed_stations:
                continue

            for edge in edges:
                destination_id = edge["destination"]

                if destination_id in self.closed_stations:
                    continue

                segment = frozenset((source_id, destination_id))

                if segment in self.closed_segments:
                    continue

                groups.union(source_id, destination_id)

        target_group = groups.find(station_id)

        return {
            name
            for other_id, name in self.stations.items()
            if (
                    other_id not in self.closed_stations
                    and groups.find(other_id) == target_group
            )
        }


if __name__ == "__main__":
    data_path = Path(__file__).parent / "data" / "network.json"

    graph = Graph.from_json(data_path)

    print("Stations loaded:", len(graph.stations))
    print("Ameerpet ID:", graph.find_station("AMEERPET"))
    print("Connections from Ameerpet:", graph.adjacency["S11"])
