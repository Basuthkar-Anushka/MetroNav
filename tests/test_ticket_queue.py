
import pytest

from ticket_queue import TicketQueue
from metronav import load_ticket_queue
from graph import Graph


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


def test_loader_skips_unknown_origin(tmp_path):
    network_file = tmp_path / "network.json"
    journeys_file = tmp_path / "journeys.txt"

    network_file.write_text(
        '''
        {
            "interchange_penalty_minutes": 4,
            "stations": [
                {"id": "A", "name": "Ameerpet"},
                {"id": "B", "name": "Begumpet"}
            ],
            "connections": []
        }
        ''',
        encoding="utf-8"
    )

    journeys_file.write_text(
        "timestamp,origin,destination,peak\n"
        "08:00,UnknownStation,Begumpet,1\n"
        "08:05,Ameerpet,Begumpet,0\n",
        encoding="utf-8"
    )

    graph = Graph.from_json(network_file)
    queue = load_ticket_queue(journeys_file, graph)

    assert len(queue) == 1
    assert queue.first_n(1)[0]["origin"] == "Ameerpet"


def test_loader_skips_unknown_destination(tmp_path):
    network_file = tmp_path / "network.json"
    journeys_file = tmp_path / "journeys.txt"

    network_file.write_text(
        '''
        {
            "interchange_penalty_minutes": 4,
            "stations": [
                {"id": "A", "name": "Ameerpet"},
                {"id": "B", "name": "Begumpet"}
            ],
            "connections": []
        }
        ''',
        encoding="utf-8"
    )

    journeys_file.write_text(
        "timestamp,origin,destination,peak\n"
        "08:00,Ameerpet,UnknownStation,1\n"
        "08:05,Ameerpet,Begumpet,0\n",
        encoding="utf-8"
    )

    graph = Graph.from_json(network_file)
    queue = load_ticket_queue(journeys_file, graph)

    assert len(queue) == 1
    assert queue.first_n(1)[0]["destination"] == "Begumpet"
