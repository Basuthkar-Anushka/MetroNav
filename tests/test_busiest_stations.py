
from busiest_stations import find_busiest_stations


def test_counts_both_origins_and_destinations(tmp_path):
    journeys = tmp_path / "journeys.txt"
    journeys.write_text(
        "timestamp,origin,destination,peak\n"
        "06:00:08,A,B,0\n"
        "06:00:17,B,C,1\n"
        "06:00:25,A,C,0\n",
        encoding="utf-8",
    )

    result, invalid = find_busiest_stations(journeys, 2)

    assert result == [("A", 2), ("B", 2)]
    assert invalid == 0


def test_skips_invalid_rows(tmp_path):
    journeys = tmp_path / "journeys.txt"
    journeys.write_text(
        "timestamp,origin,destination,peak\n"
        "06:00:08,A,B,0\n"
        "06:00:17,,C,1\n",
        encoding="utf-8",
    )

    result, invalid = find_busiest_stations(journeys, 2)

    assert result == [("A", 1), ("B", 1)]
    assert invalid == 1


def test_returns_k_busiest_stations(tmp_path):
    journeys = tmp_path / "journeys.txt"

    rows = ["timestamp,origin,destination,peak"]

    # A appears in 100 journey endpoints.
    for i in range(50):
        rows.append(f"06:{i:02d},A,B,0")
        rows.append(f"06:{i:02d},A,C,0")

    # B appears in 50 journey endpoints.
    for i in range(25):
        rows.append(f"07:{i:02d},B,C,0")

    journeys.write_text("\n".join(rows) + "\n", encoding="utf-8")

    result, invalid = find_busiest_stations(journeys, 2)

    assert result == [("A", 100), ("B", 75)]
    assert invalid == 0


def test_equal_counts_are_sorted_alphabetically(tmp_path):
    journeys = tmp_path / "journeys.txt"
    journeys.write_text(
        "timestamp,origin,destination,peak\n"
        "06:00,B,B,0\n"
        "06:01,A,A,0\n"
        "06:02,C,C,0\n",
        encoding="utf-8",
    )

    result, invalid = find_busiest_stations(journeys, 3)

    assert result == [("A", 2), ("B", 2), ("C", 2)]
    assert invalid == 0


def test_k_one_returns_only_busiest_station(tmp_path):
    journeys = tmp_path / "journeys.txt"
    journeys.write_text(
        "timestamp,origin,destination,peak\n"
        "06:00,A,A,0\n"
        "06:01,A,A,0\n"
        "06:02,B,B,0\n",
        encoding="utf-8",
    )

    result, invalid = find_busiest_stations(journeys, 1)

    assert result == [("A", 4)]
    assert invalid == 0


def test_k_zero_returns_empty_list(tmp_path):
    journeys = tmp_path / "journeys.txt"
    journeys.write_text(
        "timestamp,origin,destination,peak\n"
        "06:00,A,B,0\n",
        encoding="utf-8",
    )

    result, invalid = find_busiest_stations(journeys, 0)

    assert result == []
    assert invalid == 0
