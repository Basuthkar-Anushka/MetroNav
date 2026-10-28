import unittest

from cache import LRUCache


class TestLRUCache(unittest.TestCase):

    def test_get_missing_key(self):
        cache = LRUCache()
        self.assertIsNone(cache.get("missing"))

    def test_put_and_get(self):
        cache = LRUCache()
        cache.put("route_A", 10)
        self.assertEqual(cache.get("route_A"), 10)

    def test_update_existing_key(self):
        cache = LRUCache()
        cache.put("route_A", 10)
        cache.put("route_A", 15)
        self.assertEqual(cache.get("route_A"), 15)

    def test_evict_least_recently_used(self):
        cache = LRUCache(capacity=2)
        cache.put("A", 1)
        cache.put("B", 2)

        cache.get("A")  # A becomes most recently used
        cache.put("C", 3)  # B should be evicted

        self.assertEqual(cache.get("A"), 1)
        self.assertIsNone(cache.get("B"))
        self.assertEqual(cache.get("C"), 3)

    def test_clear(self):
        cache = LRUCache()
        cache.put("A", 1)
        cache.put("B", 2)

        cache.clear()

        self.assertIsNone(cache.get("A"))
        self.assertIsNone(cache.get("B"))

    def test_get_marks_item_as_recent(self):
        cache = LRUCache(capacity=2)
        cache.put("A", 1)
        cache.put("B", 2)

        cache.get("A")
        cache.put("C", 3)

        self.assertEqual(cache.get("A"), 1)
        self.assertIsNone(cache.get("B"))
        self.assertEqual(cache.get("C"), 3)

    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            LRUCache(capacity=0)

    def test_items_most_recent_first(self):
        cache = LRUCache(capacity=3)
        cache.put("A", 1)
        cache.put("B", 2)
        cache.put("C", 3)

        cache.get("A")

        self.assertEqual(
            cache.items_most_recent_first(),
            [("A", 1), ("C", 3), ("B", 2)]
        )


if __name__ == "__main__":
    unittest.main()
