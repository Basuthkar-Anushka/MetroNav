# MetroNav

MetroNav is a Python command-line application for navigating a metro network. It uses graph algorithms and custom data structures to find routes, suggest stations, calculate journey details, and estimate fares.

## Features

- **Station suggestions:** Search for station names using prefix matching with a Trie.
- **Fastest route:** Find a route that minimizes travel time, including interchange penalties.
- **Fewest interchanges:** Find routes prioritizing fewer line changes.
- **Cheapest route:** Find routes prioritizing the calculated fare.
- **Journey information:** Display route details, travel time, and distance.
- **Fare calculation:** Calculate fares using configurable fare slabs.
- **LRU caching:** Reuse previously calculated results to reduce repeated work.
- **Custom minimum heap:** Process route states by priority.
- **JSON data:** Load the metro network and fare configuration from files.

## Project Structure

```text
MetroNav/
├── main.py
├── graph.py
├── routing.py
├── min_heap.py
├── trie.py
├── cache.py
├── fares.py
├── data/
│   ├── network.json
│   └── fares.json
├── tests/
├── DESIGN.md
└── README.md
```

## Requirements

- Python 3
- `pytest` for running the automated tests

## Setup

1. Clone or download the project.
2. Open the project folder in PyCharm or a terminal.
3. Open a terminal in the project directory.
4. Install the test dependency if needed:

```bash
python -m pip install pytest
```

## Usage

Run the following commands from the project directory:

### Display network information

```bash
python metronav.py info
```

### Suggest stations

```bash
python metronav.py suggest Ame
```

### Find the fastest route

```bash
python metronav.py route Ameerpet Moosapet --mode fastest
```

### Find a route with fewer interchanges

```bash
python metronav.py route Ameerpet "SR Nagar" --mode fewest-interchanges
```

### Find the cheapest route

```bash
python metronav.py route Miyapur Nagole --mode cheapest
```

Station names containing spaces should be enclosed in quotation marks.

## Running Tests

Run the automated test suite from the project directory:

```bash
python -m pytest -q
```

Pytest reports the number of tests that pass or fail. Run the suite again after making changes to the application.

## Data Files

- `data/network.json` contains the metro stations and connections, including line, travel-time, and distance information.
- `data/fares.json` contains the fare configuration used by the fare calculator.

## Design and Algorithms

The project uses a weighted graph for the metro network, a Trie for station-prefix searches, a custom minimum heap for priority-based processing, and a dictionary with a doubly linked list for LRU caching.

See [DESIGN.md](DESIGN.md) for the architecture, algorithm descriptions, complexity analysis, and remaining assessment requirements.

## AI Assistance Disclosure

AI tools were used as a support resource to clarify concepts, troubleshoot errors, review code, and improve documentation. AI-generated suggestions were reviewed and adapted during development. The developer is responsible for understanding, testing, and verifying the submitted implementation.
