
import pytest

from ticket_queue import TicketQueue


def test_peak_requests_are_served_first():
    queue = TicketQueue()
    off_peak = {"id": 1, "peak": 0}
    peak = {"id": 2, "peak": 1}

    queue.enqueue(off_peak)
    queue.enqueue(peak)

    assert queue.dequeue() == peak
    assert queue.dequeue() == off_peak


def test_fifo_order_within_same_priority():
    queue = TicketQueue()
    first = {"id": 1, "peak": 1}
    second = {"id": 2, "peak": 1}

    queue.enqueue(first)
    queue.enqueue(second)

    assert queue.dequeue() == first
    assert queue.dequeue() == second


def test_first_n_does_not_remove_requests():
    queue = TicketQueue()
    queue.enqueue({"id": 1, "peak": 0})
    queue.enqueue({"id": 2, "peak": 1})

    assert queue.first_n(1) == [{"id": 2, "peak": 1}]
    assert len(queue) == 2


def test_negative_n_is_rejected():
    queue = TicketQueue()

    with pytest.raises(ValueError, match="N cannot be negative"):
        queue.first_n(-1)


def test_empty_queue_raises_error():
    queue = TicketQueue()

    with pytest.raises(IndexError):
        queue.dequeue()
