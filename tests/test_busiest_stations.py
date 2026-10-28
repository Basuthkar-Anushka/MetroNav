
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
