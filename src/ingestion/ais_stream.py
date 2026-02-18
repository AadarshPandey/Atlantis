# Connects to AIS feeds to collect ship ID signals.
# For demonstration: generates random AIS data based on the sample data format.

import random
from datetime import datetime, timedelta


# ── Sample ship database (based on known vessel tracks) ──────────────────────
_SHIP_DATABASE = [
    {"ship_id": "SHIP_1000", "base_lat": 16.53534, "base_lon": -69.42185, "direction": "NW"},
    {"ship_id": "SHIP_1001", "base_lat": 11.26284, "base_lon": -66.40861, "direction": "S"},
    {"ship_id": "SHIP_1002", "base_lat": 10.96187, "base_lon": -62.11715, "direction": "SE"},
    {"ship_id": "SHIP_1003", "base_lat": 14.85200, "base_lon": -65.30000, "direction": "E"},
    {"ship_id": "SHIP_1004", "base_lat": 12.10000, "base_lon": -68.75000, "direction": "NE"},
]


def _random_drift(base: float, max_drift: float = 0.1) -> float:
    """Add small random drift to a coordinate to simulate vessel movement."""
    return round(base + random.uniform(-max_drift, max_drift), 5)


def get_ais_data(num_ships: int = None, num_pings: int = 3) -> list[dict]:
    """
    Generate random AIS data records simulating ship position broadcasts.

    Args:
        num_ships: Number of ships to include (default: random 3–5).
        num_pings: Number of position pings per ship.

    Returns:
        List of dicts with keys: ship_id, latitude, longitude, date, time
    """
    if num_ships is None:
        num_ships = random.randint(3, 5)

    # Pick random ships from our database
    selected_ships = random.sample(_SHIP_DATABASE, min(num_ships, len(_SHIP_DATABASE)))

    now = datetime.now()
    records = []

    for ship in selected_ships:
        base_time = now - timedelta(hours=1)

        for ping in range(num_pings):
            ping_time = base_time + timedelta(minutes=30 * ping)
            record = {
                "ship_id": ship["ship_id"],
                "latitude": _random_drift(ship["base_lat"]),
                "longitude": _random_drift(ship["base_lon"]),
                "date": ping_time.strftime("%Y-%m-%d"),
                "time": ping_time.strftime("%H:%M:%S"),
            }
            records.append(record)

    print(f"  [AIS] Generated {len(records)} AIS pings from {num_ships} vessels.")
    return records


if __name__ == "__main__":
    data = get_ais_data()
    for r in data:
        print(f"  {r['ship_id']}\t{r['latitude']}\t{r['longitude']}\t{r['date']}\t{r['time']}")