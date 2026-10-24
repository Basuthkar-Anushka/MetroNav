from pathlib import Path
from fares import FareCalculator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FARE_FILE = PROJECT_ROOT / "data" / "fares.json"

calculator = FareCalculator.from_json(FARE_FILE)

# First two slabs
assert calculator.calculate_fare(1) == 10
assert calculator.calculate_fare(2) == 10
assert calculator.calculate_fare(3) == 20
assert calculator.calculate_fare(4) == 20

# A few later slabs
assert calculator.calculate_fare(5) == 30
assert calculator.calculate_fare(10) == 50
assert calculator.calculate_fare(20) == 80
assert calculator.calculate_fare(40) == 120
assert calculator.calculate_fare(100) == 130

# Negative distance should be rejected
try:
    calculator.calculate_fare(-1)
    raise AssertionError("Negative distance should raise ValueError")
except ValueError:
    pass

print("All fare tests passed!")
