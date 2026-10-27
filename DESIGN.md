# MetroNav — Design Document

## 1. Project Overview

MetroNav is a Python command-line application that helps users navigate a metro network. It loads station and connection data from JSON files, suggests stations using prefix search, calculates routes, estimates journey time and distance, and calculates fares.

The project uses data structures and algorithms to organize the network, search for routes, provide station suggestions, and cache previously calculated results.

## 2. Project Structure

- `metronav.py` — Command-line interface and application entry point.
- `graph.py` — Loads the metro network and provides station lookup.
- `routing.py` — Calculates routes between stations.
- `min_heap.py` — Implements a custom minimum heap for priority-based processing.
- `trie.py` — Implements station prefix search and removal.
- `cache.py` — Implements a Least Recently Used (LRU) cache.
- `fares.py` — Calculates fares using configured fare slabs.
- `data/network.json` — Stores station and connection information.
- `data/fares.json` — Stores fare slabs and currency information.
- `tests/` — Contains automated and manual tests.

## 3. Graph Representation

The metro network is represented as a weighted, undirected graph using an adjacency list.

Each station has an ID and a name. The graph stores station IDs mapped to their names and normalized station names mapped to their IDs.

Each connection records:
- Destination station ID
- Metro line
- Travel time in minutes
- Distance in kilometres

Connections are stored in both directions.

If V represents the number of stations and E represents the number of connections, graph construction takes O(V + E) time. Station lookup takes O(1) average time using a dictionary.

## 4. Trie for Station Suggestions

The Trie in `trie.py` supports prefix-based station suggestions.

Each Trie node contains:
- A dictionary of child nodes
- A set of station names ending at that node

Station names are normalized with `casefold()` for case-insensitive searching. The original spelling is retained for display.

The prefix search follows the characters of the requested prefix. If the prefix exists, the Trie collects matching station names and returns them in case-insensitive alphabetical order.

For a prefix of length P, locating the matching node takes O(P) time. Sorting R matching results takes O(R log R) time, in addition to traversing the relevant subtree.

The Trie supports insertion, prefix search, and removal.

## 5. Minimum Heap

The custom minimum heap is implemented in `min_heap.py` using a Python list.

The smallest item is maintained at the root.

- `push()` inserts an item and moves it upward to restore heap order.
- `pop()` removes the smallest item and restores heap order by moving an item downward.
- `is_empty()` checks whether the heap contains any items.

Insertion and removal each take O(log N) time, while checking whether the heap is empty takes O(1) time.

The heap is used by the routing algorithm to process the most promising route state first.

## 6. Route Calculation

The router uses the graph and minimum heap to search for a route.

A route result contains station IDs, the line used for each leg, total travel time, total distance, and interchange information.

The routing state includes both the current station and the current metro line. This is important because changing lines can add an interchange penalty.

### Fastest route

The fastest-route algorithm minimizes total travel time, including the configured penalty for changing metro lines.

Dijkstra's algorithm is suitable because travel times and interchange penalties are non-negative.

### Fewest-interchanges route

This mode prioritizes the route with the fewest line changes. Travel time is used as a secondary criterion when comparing routes with the same number of interchanges.

### Cheapest route

This mode aims to select the route with the lowest fare calculated from the configured fare slabs, using travel time as a secondary criterion.

The correctness of the fewest-interchanges and cheapest modes should be verified with tests that compare alternative routes with known expected results.

## 7. Fare Calculation

The fare calculator in `fares.py` loads fare information from `data/fares.json`.

It checks the journey distance against the configured fare slabs and returns the fare for the first matching maximum-distance boundary.

Negative distances raise a `ValueError`.

If there are S fare slabs, the current linear search takes O(S) time. Fare slabs should be maintained in the correct order.

## 8. LRU Cache

The cache in `cache.py` uses a dictionary and a doubly linked list.

The dictionary provides quick access to cached entries. The linked list tracks usage order, with the most recently used entry at the front and the least recently used entry at the back.

When an entry is accessed, it becomes the most recently used. When the cache exceeds its capacity, the least recently used entry is evicted.

The cache supports retrieving values, inserting or updating values, and clearing its contents.

Cache `get()` and `put()` operations take O(1) average time.

The router caches route results to avoid repeating calculations. Different routing modes must use distinct cache keys. If network closures are introduced, cached routes must be invalidated when the network changes.

## 9. Command-Line Interface

The application uses Python's `argparse` module.

Examples of the current CLI commands are:

```bash
python metronav.py info
python metronav.py suggest Ame
python metronav.py route Ameerpet Moosapet --mode fastest
python metronav.py route Ameerpet "SR Nagar" --mode fewest-interchanges
python metronav.py route Miyapur Nagole --mode cheapest
```

Station names containing spaces should be enclosed in quotes in the terminal.

The `info` command displays network information, `suggest` returns station suggestions, and `route` requests a journey between two stations.

The route command is intended to display journey details, including line changes, travel time, distance, and fare.

## 10. Error Handling

The application handles common file and data errors and displays an explanatory message when a command cannot be completed.

Unknown station names should produce a clear message instead of attempting to route from an invalid station.

Additional testing should verify malformed JSON, missing data fields, invalid station references, and invalid fare data.

## 11. Testing

Testing should cover both normal behaviour and edge cases.

Important test cases include:

- Minimum heap returns items in ascending order.
- Station lookup is case-insensitive.
- Trie prefix search returns correct suggestions.
- Trie removal handles existing and missing names.
- Fare calculation handles slab boundaries and negative distances.
- LRU cache correctly updates entries and evicts the least recently used entry.
- Route caching returns the expected results.
- Fastest, fewest-interchanges, and cheapest modes return the correct routes.
- Line changes include the correct interchange penalty.
- Unknown stations and identical origin and destination are handled correctly.

Previously, automated cache and route-cache tests passed, and manual checks were performed for the Trie, fare calculator, and a sample fastest route. The full test suite should be rerun after the latest routing changes.

## 12. Remaining Assessment Requirements

The following requirements must not be considered complete until they have been implemented and tested:

- Closing and reopening stations and track segments.
- Invalidating cached routes after network changes.
- Finding disconnected zones using Union-Find.
- Identifying critical stations using Tarjan's algorithm.
- Finding stations reachable within a time limit.
- Planning network expansion using Kruskal's algorithm and Union-Find.
- Identifying the busiest stations using a size-K minimum heap.
- Processing ticket requests by priority and arrival order.
- Implementing any additional required CLI commands.
- Meeting the assessment's automated test-count requirement.
- Completing the README and reviewing Git history.


## 13. Complexity Summary


| Operation              | Time complexity                                                  |
|------------------------|------------------------------------------------------------------|
| Graph construction     | O(V + E)                                                         |
| Station lookup         | O(1) average                                                     |
| Trie prefix traversal  | O(P)                                                             |
| Sorting R suggestions  | O(R log R)                                                       |
| Heap insertion         | O(log N)                                                         |
| Heap removal           | O(log N)                                                         |
| LRU cache get/put      | O(1) average                                                     |
| Fare slab lookup       | O(S)                                                             |
| Dijkstra-style routing | Typically O((V + E) log V), adjusted for station-and-line states |


V is the number of stations, E is the number of connections, P is the prefix length, R is the number of suggestions, N is the heap or cache size, and S is the number of fare slabs.

## 14. AI Assistance Disclosure

## AI Assistance Disclosure

AI tools were used as a support resource during the development of MetroNav. They helped clarify concepts, troubleshoot errors, review code, and improve project documentation. The implementation, testing, and verification of the project features were carried out as part of the development process. AI-generated suggestions were reviewed and adapted to fit the project requirements.
