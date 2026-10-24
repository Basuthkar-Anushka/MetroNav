
from min_heap import MinHeap
from cache import LRUCache


class Router:
    def __init__(self, graph, fare_calculator=None):
        self.graph = graph
        self.fare_calculator = fare_calculator
        self.route_cache = LRUCache(capacity=10)

    def get_neighbors(self, station_id):
        return self.graph.adjacency[station_id]

    def find_route(self, origin_name, destination_name, mode="fastest"):
        if mode not in ("fastest", "fewest-interchanges", "cheapest"):
            raise ValueError("Unknown route mode")

        origin = self.graph.find_station(origin_name)
        destination = self.graph.find_station(destination_name)

        if origin is None or destination is None:
            return None

        if mode == "cheapest" and self.fare_calculator is None:
            raise ValueError("Fare calculator is required for cheapest mode")

        cache_key = (origin, destination, mode)
        cached_result = self.route_cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        if origin == destination:
            result = {
                "minutes": 0,
                "stations": [origin],
                "lines": [],
                "distance_km": 0,
                "interchanges": 0,
            }
            self.route_cache.put(cache_key, result)
            return result

        if mode == "cheapest":
            result = self._cheapest_route(origin, destination)
        else:
            result = self._single_best_route(origin, destination, mode)

        if result is not None:
            self.route_cache.put(cache_key, result)

        return result

    def shortest_time(self, origin_name, destination_name):
        """Keep compatibility with the original fastest-route method."""
        return self.find_route(origin_name, destination_name, "fastest")

    def _single_best_route(self, origin, destination, mode):
        # A state includes the station and the line currently being used.
        start = (origin, None)
        best = {start: (0, 0)}  # (interchanges, minutes)
        previous = {}

        heap = MinHeap()
        heap.push((0, 0, origin, ""))

        while not heap.is_empty():
            first, minutes, station, line_key = heap.pop()
            current_line = line_key or None
            state = (station, current_line)

            if mode == "fastest":
                if minutes != best.get(state, (None, None))[1]:
                    continue
            else:
                if (first, minutes) != best.get(state):
                    continue

            for edge in self.get_neighbors(station):
                next_station = edge["destination"]
                next_line = edge["line"]

                changed_line = (
                    current_line is not None and current_line != next_line
                )
                new_interchanges = first if mode == "fastest" else first
                if mode == "fewest-interchanges" and changed_line:
                    new_interchanges += 1

                new_minutes = minutes + edge["minutes"]
                if changed_line:
                    new_minutes += self.graph.interchange_penalty

                next_state = (next_station, next_line)

                if mode == "fastest":
                    candidate = (0, new_minutes)
                    old = best.get(next_state)
                    if old is not None and old[1] <= new_minutes:
                        continue
                    priority = (0, new_minutes)
                else:
                    candidate = (new_interchanges, new_minutes)
                    old = best.get(next_state)
                    if old is not None and old <= candidate:
                        continue
                    priority = candidate

                best[next_state] = candidate
                previous[next_state] = state
                heap.push((priority[0], priority[1], next_station, next_line))

        destinations = [s for s in best if s[0] == destination]
        if not destinations:
            return None

        if mode == "fastest":
            best_state = min(destinations, key=lambda s: best[s][1])
            total_minutes = best[best_state][1]
        else:
            best_state = min(destinations, key=lambda s: best[s])
            total_minutes = best[best_state][1]

        states = []
        state = best_state
        while state is not None:
            states.append(state)
            state = previous.get(state)
        states.reverse()

        lines = [state[1] for state in states[1:]]
        distance = self._calculate_distance(states, lines)
        interchanges = sum(
            1 for i in range(1, len(lines)) if lines[i] != lines[i - 1]
        )

        return {
            "minutes": total_minutes,
            "stations": [state[0] for state in states],
            "lines": lines,
            "distance_km": distance,
            "interchanges": interchanges,
        }

    def _cheapest_route(self, origin, destination):
        # Keep routes that trade off distance and time. Two routes to the
        # same station/line may have different distances and travel times.
        labels = {}
        labels_at_state = {}
        next_label_id = 0

        start_state = (origin, None)
        labels[next_label_id] = {
            "state": start_state,
            "distance": 0.0,
            "minutes": 0,
            "previous": None,
        }
        labels_at_state[start_state] = [next_label_id]

        heap = MinHeap()
        heap.push((0.0, 0, next_label_id))

        while not heap.is_empty():
            _, _, label_id = heap.pop()
            label = labels[label_id]
            station, current_line = label["state"]

            for edge in self.get_neighbors(station):
                next_station = edge["destination"]
                next_line = edge["line"]
                changed_line = (
                    current_line is not None and current_line != next_line
                )

                new_distance = label["distance"] + edge["km"]
                new_minutes = label["minutes"] + edge["minutes"]
                if changed_line:
                    new_minutes += self.graph.interchange_penalty

                next_state = (next_station, next_line)
                existing_ids = labels_at_state.setdefault(next_state, [])

                # An existing route dominates this route if it is no longer
                # and no slower. Such a route can never be the better choice.
                dominated = any(
                    labels[old_id]["distance"] <= new_distance
                    and labels[old_id]["minutes"] <= new_minutes
                    for old_id in existing_ids
                )
                if dominated:
                    continue

                # Remove routes that this new route improves upon.
                labels_at_state[next_state] = [
                    old_id for old_id in existing_ids
                    if not (
                        new_distance <= labels[old_id]["distance"]
                        and new_minutes <= labels[old_id]["minutes"]
                    )
                ]

                next_label_id += 1
                labels[next_label_id] = {
                    "state": next_state,
                    "distance": new_distance,
                    "minutes": new_minutes,
                    "previous": label_id,
                }
                labels_at_state[next_state].append(next_label_id)
                heap.push((new_distance, new_minutes, next_label_id))

        destination_labels = [
            label_id
            for state, ids in labels_at_state.items()
            if state[0] == destination
            for label_id in ids
        ]
        if not destination_labels:
            return None

        def fare_for(label_id):
            return self.fare_calculator.calculate_fare(
                labels[label_id]["distance"]
            )

        usable_labels = [
            label_id for label_id in destination_labels
            if fare_for(label_id) is not None
        ]
        if not usable_labels:
            return None

        best_id = min(
            usable_labels,
            key=lambda label_id: (
                fare_for(label_id),
                labels[label_id]["minutes"],
            ),
        )

        path = []
        current_id = best_id
        while current_id is not None:
            path.append(labels[current_id]["state"])
            current_id = labels[current_id]["previous"]
        path.reverse()

        lines = [state[1] for state in path[1:]]
        distance = self._calculate_distance(path, lines)
        interchanges = sum(
            1 for i in range(1, len(lines)) if lines[i] != lines[i - 1]
        )

        return {
            "minutes": labels[best_id]["minutes"],
            "stations": [state[0] for state in path],
            "lines": lines,
            "distance_km": distance,
            "interchanges": interchanges,
        }

    def _calculate_distance(self, states, lines):
        total_distance = 0.0

        for i in range(len(states) - 1):
            current_station = states[i][0]
            next_station = states[i + 1][0]
            line = lines[i]

            for edge in self.get_neighbors(current_station):
                if (
                    edge["destination"] == next_station
                    and edge["line"] == line
                ):
                    total_distance += edge["km"]
                    break

        return total_distance
