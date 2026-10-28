
import unittest
from pathlib import Path

from graph import Graph
from routing import Router


class TestRouteCache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project_folder = Path(__file__).resolve().parent.parent
        network_file = project_folder / "data" / "network.json"

        cls.graph = Graph.from_json(network_file)

    def setUp(self):
        project_folder = Path(__file__).resolve().parent.parent
        network_file = project_folder / "data" / "network.json"

        # Create a fresh graph for every test.
        self.graph = Graph.from_json(network_file)
        self.router = Router(self.graph)


    def test_repeated_route_returns_same_result(self):
        first_route = self.router.shortest_time(
            "Ameerpet", "Moosapet"
        )
        second_route = self.router.shortest_time(
            "Ameerpet", "Moosapet"
        )

        self.assertIsNotNone(first_route)
        self.assertEqual(first_route, second_route)

    def test_repeated_route_uses_cache(self):
        self.router.shortest_time("Ameerpet", "Moosapet")

        cache_size_after_first_request = len(
            self.router.route_cache.cache
        )

        self.router.shortest_time("Ameerpet", "Moosapet")

        cache_size_after_second_request = len(
            self.router.route_cache.cache
        )

        self.assertEqual(cache_size_after_first_request, 1)
        self.assertEqual(cache_size_after_second_request, 1)


    def test_closing_station_clears_route_cache(self):
        self.router.shortest_time("Ameerpet", "Moosapet")
        self.assertGreater(len(self.router.route_cache.cache), 0)

        self.router.close_station("Ameerpet")

        self.assertEqual(len(self.router.route_cache.cache), 0)

    def test_closing_segment_clears_route_cache(self):
        self.router.shortest_time("Ameerpet", "Moosapet")
        self.assertGreater(len(self.router.route_cache.cache), 0)

        # Find an actual track segment in the graph.
        station_id = next(iter(self.graph.adjacency))
        edge = self.graph.adjacency[station_id][0]
        destination_id = edge["destination"]

        station_a = self.graph.stations[station_id]
        station_b = self.graph.stations[destination_id]

        self.router.close_segment(station_a, station_b)

        self.assertEqual(len(self.router.route_cache.cache), 0)


if __name__ == "__main__":
    unittest.main()
