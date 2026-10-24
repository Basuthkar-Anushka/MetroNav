
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
        # Give each test a fresh router and an empty cache.
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


if __name__ == "__main__":
    unittest.main()
