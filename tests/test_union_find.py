
from union_find import UnionFind


def test_items_start_in_separate_groups():
    groups = UnionFind(["A", "B", "C"])

    assert not groups.connected("A", "B")


def test_union_connects_two_items():
    groups = UnionFind(["A", "B", "C"])

    groups.union("A", "B")

    assert groups.connected("A", "B")
    assert not groups.connected("A", "C")


def test_transitive_connections():
    groups = UnionFind(["A", "B", "C"])

    groups.union("A", "B")
    groups.union("B", "C")

    assert groups.connected("A", "C")


def test_union_returns_false_for_already_connected_items():
    groups = UnionFind(["A", "B"])

    assert groups.union("A", "B")
    assert not groups.union("A", "B")
