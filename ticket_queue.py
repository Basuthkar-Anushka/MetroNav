
class FIFOQueue:
    """A simple FIFO queue implemented with a list and front index."""

    def __init__(self):
        self._items = []
        self._front = 0

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Cannot dequeue from an empty queue")

        item = self._items[self._front]
        self._front += 1

        # Compact occasionally to avoid retaining consumed items.
        if self._front >= 50 and self._front * 2 >= len(self._items):
            self._items = self._items[self._front:]
            self._front = 0

        return item

    def is_empty(self):
        return self._front >= len(self._items)

    def __len__(self):
        return len(self._items) - self._front

    def items(self):
        """Return queued items in FIFO order without removing them."""
        return self._items[self._front:]


class TicketQueue:
    """Serve peak-hour requests before off-peak requests."""

    def __init__(self):
        self._peak = FIFOQueue()
        self._off_peak = FIFOQueue()

    def enqueue(self, request):
        peak = request.get("peak")

        if peak not in (0, 1):
            raise ValueError("Request peak must be 0 or 1")

        if peak == 1:
            self._peak.enqueue(request)
        else:
            self._off_peak.enqueue(request)

    def dequeue(self):
        if not self._peak.is_empty():
            return self._peak.dequeue()

        if not self._off_peak.is_empty():
            return self._off_peak.dequeue()

        raise IndexError("Cannot dequeue from an empty ticket queue")

    def is_empty(self):
        return self._peak.is_empty() and self._off_peak.is_empty()

    def __len__(self):
        return len(self._peak) + len(self._off_peak)

    def first_n(self, n):
        """Return the next N requests without removing them."""
        if n < 0:
            raise ValueError("N cannot be negative")

        requests = self._peak.items() + self._off_peak.items()
        return requests[:n]
