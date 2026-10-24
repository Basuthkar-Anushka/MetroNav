class MinHeap:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        # Put the new item at the end.
        self.items.append(item)

        # Move it upward while it is smaller than its parent.
        child = len(self.items) - 1

        while child > 0:
            parent = (child - 1) // 2

            if self.items[parent] <= self.items[child]:
                break

            self.items[parent], self.items[child] = (
                self.items[child],
                self.items[parent],
            )

            child = parent

    def pop(self):
        if self.is_empty():
            raise IndexError("Cannot pop from an empty heap")

        smallest = self.items[0]
        last_item = self.items.pop()

        if self.items:
            self.items[0] = last_item
            self._move_down(0)

        return smallest

    def _move_down(self, parent):
        size = len(self.items)

        while True:
            smallest = parent
            left = 2 * parent + 1
            right = 2 * parent + 2

            if (
                left < size
                and self.items[left] < self.items[smallest]
            ):
                smallest = left

            if (
                right < size
                and self.items[right] < self.items[smallest]
            ):
                smallest = right

            if smallest == parent:
                break

            self.items[parent], self.items[smallest] = (
                self.items[smallest],
                self.items[parent],
            )

            parent = smallest


if __name__ == "__main__":
    heap = MinHeap()

    for number in [8, 3, 6, 1]:
        heap.push(number)

    while not heap.is_empty():
        print(heap.pop())
