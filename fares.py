import json
from decimal import Decimal, InvalidOperation


class FareCalculator:
    def __init__(self, fare_data):
        self.fare_slabs = fare_data["slabs"]
        self.currency = fare_data["currency"]

    @classmethod
    def from_json(cls, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            fare_data = json.load(file)

        return cls(fare_data)

    from decimal import Decimal, InvalidOperation

    def calculate_fare(self, distance_km):
        try:
            distance = Decimal(str(distance_km))
        except (InvalidOperation, ValueError):
            raise ValueError("Invalid distance")

        if not distance.is_finite():
            raise ValueError("Distance must be finite")

        if distance < 0:
            raise ValueError("Distance cannot be negative")

        for slab in self.fare_slabs:
            if distance <= Decimal(str(slab["max_km"])):
                return slab["fare"]

        return None
