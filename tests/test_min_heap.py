
import pytest
from min_heap import MinHeap


def test_pop_from_empty_heap_raises_error():
    heap = MinHeap()

    with pytest.raises(IndexError, match="Cannot pop from an empty heap"):
        heap.pop()


def test_pop_returns_smallest_item_first():
    heap = MinHeap()

    for number in [8, 3, 6, 1]:
        heap.push(number)

    assert heap.pop() == 1
    assert heap.pop() == 3
    assert heap.pop() == 6
    assert heap.pop() == 8


def test_heap_is_empty_after_all_items_are_popped():
    heap = MinHeap()

    heap.push(5)
    heap.pop()

    assert heap.is_empty()
