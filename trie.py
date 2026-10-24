class TrieNode:
    def __init__(self):
        self.children = {}
        self.station_names = set()


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.station_names = set()

    def insert(self, name):
        normalized_name = name.casefold()
        current = self.root

        for character in normalized_name:
            if character not in current.children:
                current.children[character] = TrieNode()
            current = current.children[character]

        current.station_names.add(name)
        self.station_names.add(name)

    def search_prefix(self, prefix):
        normalized_prefix = prefix.casefold()
        current = self.root

        for character in normalized_prefix:
            if character not in current.children:
                return []
            current = current.children[character]

        results = []

        def collect(node):
            results.extend(node.station_names)

            for child in node.children.values():
                collect(child)

        collect(current)
        return sorted(results, key=str.casefold)

    def remove(self, name):
        normalized_name = name.strip().casefold()

        # Find the original spelling stored in the Trie.
        original_name = next(
            (
                station
                for station in self.station_names
                if station.strip().casefold() == normalized_name
            ),
            None,
        )

        if original_name is None:
            return False

        def delete(node, index):
            if index == len(normalized_name):
                node.station_names.remove(original_name)
            else:
                character = normalized_name[index]
                child = node.children[character]

                should_delete_child = delete(child, index + 1)

                if should_delete_child:
                    del node.children[character]

            return not node.station_names and not node.children

        delete(self.root, 0)
        self.station_names.remove(original_name)
        return True
