import json
from pathlib import Path



class Graph:
    def __init__(self, network_data):
        # Time added when a passenger changes metro lines.
        self.interchange_penalty = network_data[
            "interchange_penalty_minutes"
        ]

        # Station ID -> station name.
        self.stations = {}

        # Normalized station name -> station ID.
        self.name_to_id = {}

        # Station ID -> list of neighbouring connections.
        self.adjacency = {}

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
        with open(file_path, "r", encoding="utf-8") as file:
            network_data = json.load(file)

        return cls(network_data)

    def find_station(self, name):
        normalized_name = name.strip().casefold()
        return self.name_to_id.get(normalized_name)


if __name__ == "__main__":
    data_path = Path(__file__).parent / "data" / "network.json"

    graph = Graph.from_json(data_path)

    print("Stations loaded:", len(graph.stations))
    print("Ameerpet ID:", graph.find_station("AMEERPET"))
    print("Connections from Ameerpet:", graph.adjacency["S11"])
