
def find_critical_stations(graph):
    """Return station names whose removal disconnects the network."""
    active = [
        station_id
        for station_id in graph.stations
        if station_id not in graph.closed_stations
    ]

    active_set = set(active)
    adjacency = {station_id: [] for station_id in active}

    # Build an undirected view of the currently open network.
    for station_id in active:
        for edge in graph.adjacency[station_id]:
            neighbor = edge["destination"]

            if (
                neighbor in active_set
                and neighbor not in graph.closed_stations
                and frozenset((station_id, neighbor))
                not in graph.closed_segments
            ):
                if neighbor not in adjacency[station_id]:
                    adjacency[station_id].append(neighbor)
                if station_id not in adjacency[neighbor]:
                    adjacency[neighbor].append(station_id)

    discovery = {}
    low = {}
    parent = {}
    critical = set()
    clock = 0

    # Iterative depth-first search avoids recursion-depth problems.
    for start in active:
        if start in discovery:
            continue

        clock += 1
        discovery[start] = low[start] = clock
        parent[start] = None
        stack = [(start, iter(adjacency[start]))]
        root_children = 0

        while stack:
            node, neighbors = stack[-1]

            try:
                neighbor = next(neighbors)
            except StopIteration:
                stack.pop()
                ancestor = parent[node]

                if ancestor is not None:
                    low[ancestor] = min(low[ancestor], low[node])

                    if (
                        parent[ancestor] is not None
                        and low[node] >= discovery[ancestor]
                    ):
                        critical.add(ancestor)

                elif root_children > 1:
                    critical.add(node)

                continue

            if neighbor not in discovery:
                parent[neighbor] = node

                if parent[node] is None:
                    root_children += 1

                clock += 1
                discovery[neighbor] = low[neighbor] = clock
                stack.append((neighbor, iter(adjacency[neighbor])))

            elif neighbor != parent[node]:
                low[node] = min(low[node], discovery[neighbor])

    return sorted(graph.stations[station_id] for station_id in critical)
