
from pathlib import Path

from fares import FareCalculator


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FARE_FILE = PROJECT_ROOT / "data" / "fares.json"


def build_calculator():
    return FareCalculator.from_json(FARE_FILE)


def test_first_fare_slabs():
    calculator = build_calculator()

    assert calculator.calculate_fare(1) == 10
    assert calculator.calculate_fare(2) == 10
    assert calculator.calculate_fare(3) == 20
    assert calculator.calculate_fare(4) == 20


def test_later_fare_slabs():
    calculator = build_calculator()

    assert calculator.calculate_fare(5) == 30
    assert calculator.calculate_fare(10) == 50
    assert calculator.calculate_fare(20) == 80
    assert calculator.calculate_fare(40) == 120
    assert calculator.calculate_fare(100) == 130


def test_negative_distance_raises_value_error():
    calculator = build_calculator()

    try:
        calculator.calculate_fare(-1)
    except ValueError:
        pass
    else:
        assert False, "Negative distance should raise ValueError"


def test_fare_at_slab_boundaries():
    from pathlib import Path
    from fares import FareCalculator

    project_root = Path(__file__).resolve().parent.parent
    fare_file = project_root / "data" / "fares.json"
    calculator = FareCalculator.from_json(fare_file)

    assert calculator.calculate_fare(2) == 10
    assert calculator.calculate_fare(2.01) == 20
    assert calculator.calculate_fare(4) == 20
    assert calculator.calculate_fare(4.01) == 30
    assert calculator.calculate_fare(45) == 120
    assert calculator.calculate_fare(45.01) == 130
