
class CacheNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.previous = None
        self.next = None


class LRUCache:
    def __init__(self, capacity=10):
        if capacity < 1:
            raise ValueError("Cache capacity must be at least 1")

        self.capacity = capacity
        self.cache = {}

        # Boundary nodes for the doubly linked list
        self.head = CacheNode(None, None)
        self.tail = CacheNode(None, None)

        self.head.next = self.tail
        self.tail.previous = self.head

    def _remove_node(self, node):
        previous_node = node.previous
        next_node = node.next

        previous_node.next = next_node
        next_node.previous = previous_node

    def _add_to_front(self, node):
        first_node = self.head.next

        node.previous = self.head
        node.next = first_node

        self.head.next = node
        first_node.previous = node

    def get(self, key):
        if key not in self.cache:
            return None

        node = self.cache[key]

        # This entry has just been used, so mark it most recent.
        self._remove_node(node)
        self._add_to_front(node)

        return node.value

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value

            self._remove_node(node)
            self._add_to_front(node)
            return

        node = CacheNode(key, value)
        self.cache[key] = node
        self._add_to_front(node)

        if len(self.cache) > self.capacity:
            least_recent_node = self.tail.previous
            self._remove_node(least_recent_node)
            del self.cache[least_recent_node.key]

    def clear(self):
        # Remove all cached entries.
        self.cache.clear()
        self.head.next = self.tail
        self.tail.previous = self.head
