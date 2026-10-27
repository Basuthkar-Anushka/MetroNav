
class UnionFind:
    def __init__(self, items):
        self.parent = {item: item for item in items}
        self.rank = {item: 0 for item in items}

    def find(self, item):
        if item not in self.parent:
            raise KeyError(f"Unknown item: {item}")

        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])

        return self.parent[item]

    def union(self, first, second):
        root_first = self.find(first)
        root_second = self.find(second)

        if root_first == root_second:
            return False

        if self.rank[root_first] < self.rank[root_second]:
            root_first, root_second = root_second, root_first

        self.parent[root_second] = root_first

        if self.rank[root_first] == self.rank[root_second]:
            self.rank[root_first] += 1

        return True

    def connected(self, first, second):
        return self.find(first) == self.find(second)
