# MetroNav — Design Document

## 1. Data Structures and Algorithms

MetroNav models the metro network as a weighted, undirected graph stored with an adjacency list. This supports efficient neighbor traversal and represents bidirectional connections naturally. Dictionaries provide average O(1) station lookup.

A **Trie** supports case-insensitive station autocomplete without scanning every station for each prefix. Insertion and prefix lookup take O(L) time, where L is the station-name or prefix length, excluding the time needed to collect and sort results. Trie space is O(T), where T is the total number of characters stored, including node and child-map overhead.

The custom **binary min-heap** supports priority-based processing in routing and other ranking operations. `push` and `pop` take O(log N) time; inspecting the heap takes O(1). Heap storage is O(N).

The **LRU cache** combines a dictionary with a doubly linked list, allowing average O(1) `get` and `put` operations. It stores up to 10 route results keyed by origin, destination, and routing mode. Network changes clear the cache to prevent stale results.

**Union-Find**, with path compression and union by rank, supports connected-component analysis and Kruskal's minimum-cost network expansion. Its operations take O(α(V)) amortized time, where α is the inverse Ackermann function.

## 2. Routing and Network Algorithms

- **Fastest route:** Dijkstra's algorithm with a custom min-heap minimizes travel time, including interchange penalties.
- **Fewest interchanges:** A priority search minimizes line changes first and travel time second.
- **Cheapest route:** Candidate routes are compared by fare slab, then travel time. Because multiple distances may fall within the same fare slab, the implementation considers distance/time alternatives rather than assuming the shortest distance always produces the cheapest result.
- **Articulation points:** Iterative Tarjan DFS identifies critical stations in O(V + E) time and O(V + E) space, including traversal state and graph storage.
- **Network expansion:** Kruskal's algorithm sorts M candidate tracks in O(M log M) time and uses Union-Find to select tracks that connect components. Union-Find processing adds near-linear amortized overhead after sorting.

For routing, let V′ and E′ represent the vertices and transitions in the expanded graph of station-and-line states. Heap-based Dijkstra-style routing typically takes O((V′ + E′) log V′) time and O(V′ + E′) space. Fewest-interchanges routing has a similar bound when implemented with a priority queue over expanded states. Cheapest routing may retain multiple non-dominated distance/time labels; its worst-case time and space can be larger because the number of labels is not necessarily bounded by one per station.

## 3. Limitations and Possible Improvements

The application relies on the supplied network, fare slabs, and journey records; it does not incorporate live delays or service updates. Cheapest-route search can retain multiple candidate labels, increasing resource use on larger networks. Trie suggestions require sorting when results are returned. Error handling and algorithm correctness should continue to be tested against malformed data, closures, disconnected networks, and unusual inputs.

With more time, I would add broader randomized and edge-case tests, benchmark larger networks, improve route-search pruning, and strengthen validation of fare and journey data. I would also review all CLI commands and persistence behavior against the assessment checklist and document any remaining limitations.

## 4. Testing and AI Assistance Disclosure

The latest test result reported during development was **79 passing tests**. Manual checks also confirmed time-limited reachability, persistent station closures, and avoidance of a closed segment when an alternative route exists.&#x20;

ChatGPT was used to explain algorithms, suggest tests, help troubleshoot errors, and review documentation. I tested suggested changes, adapted code to the project, and corrected issues identified during development, including CLI command usage and tests for cheapest-route tie-breaking and fewest-interchange behavior. I remain responsible for verifying the final implementation and understanding the submitted code.
