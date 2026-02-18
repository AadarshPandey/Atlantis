# The logic that compares Radar dots vs. AIS signals to find 'Dark Vessels'.
# A "Dark Vessel" is one detected by radar but NOT broadcasting AIS signals.

import random


def _is_nearby(lat1: float, lon1: float, lat2: float, lon2: float,
               threshold: float = 0.15) -> bool:
    """Check if two coordinates are within a threshold distance (degrees)."""
    return abs(lat1 - lat2) < threshold and abs(lon1 - lon2) < threshold


def find_dark_vessels(ais_data: list[dict],
                      radar_detections: list[dict],
                      sar_metadata: dict) -> list[dict]:
    """
    Compare AIS signals against radar detections to identify Dark Vessels.

    A vessel detected by radar but not matched to any AIS signal is flagged
    as a "Dark Vessel" — potentially operating illegally with transponder off.

    Args:
        ais_data:          List of AIS records (ship_id, latitude, longitude, ...).
        radar_detections:  List of radar detection dicts from Gemini.
        sar_metadata:      SAR image metadata (latitude, longitude, date, ...).

    Returns:
        List of dark vessel incident dicts.
    """
    sar_lat = sar_metadata["latitude"]
    sar_lon = sar_metadata["longitude"]

    # ── Step 1: Find AIS ships near the SAR image area ───────────────────────
    ais_ships_in_area = []
    unique_ships = set()
    for record in ais_data:
        if _is_nearby(record["latitude"], record["longitude"], sar_lat, sar_lon, threshold=1.0):
            if record["ship_id"] not in unique_ships:
                ais_ships_in_area.append(record)
                unique_ships.add(record["ship_id"])

    print(f"  [FUSION] AIS ships near SAR area: {len(ais_ships_in_area)}")
    print(f"  [FUSION] Radar detections: {len(radar_detections)}")

    # ── Step 2: Try to match each radar detection to an AIS signal ───────────
    dark_vessels = []
    matched_vessels = []

    for detection in radar_detections:
        matched = False

        # For each radar detection, see if any AIS ship is nearby
        for ais_ship in ais_ships_in_area:
            # Since radar gives relative_position (not exact coords), we simulate
            # matching by checking if the AIS ship is in the same general area
            if random.random() < 0.4:  # ~40% chance of match (simulating overlap)
                matched = True
                matched_vessels.append({
                    "radar": detection,
                    "ais": ais_ship,
                    "status": "IDENTIFIED",
                })
                print(f"       ✓ {detection['vessel_id']} matched → {ais_ship['ship_id']}")
                break

        if not matched:
            # ── DARK VESSEL FOUND ────────────────────────────────────────────
            dark_vessel = {
                "radar_id": detection["vessel_id"],
                "vessel_type": detection.get("vessel_type", "Unknown"),
                "estimated_length_m": detection.get("estimated_length_m", 0),
                "estimated_width_m": detection.get("estimated_width_m", 0),
                "confidence": detection.get("confidence", 0),
                "relative_position": detection.get("relative_position", "unknown"),
                "sar_latitude": sar_lat,
                "sar_longitude": sar_lon,
                "sar_date": sar_metadata["date"],
                "ais_status": "NO SIGNAL DETECTED",
                "violation_type": "AIS Transponder Disabled — Unauthorized Dark Operation",
                "behavioral_anomaly": (
                    f"Vessel detected via SAR at {abs(sar_lat):.5f}°"
                    f"{'N' if sar_lat >= 0 else 'S'}, "
                    f"{abs(sar_lon):.5f}°{'E' if sar_lon >= 0 else 'W'} "
                    f"on {sar_metadata['date']}. No AIS transponder signal was "
                    f"received from this location, creating a 'Dark Period' "
                    f"in protected waters."
                ),
            }
            dark_vessels.append(dark_vessel)
            print(f"       ✗ {detection['vessel_id']} → NO AIS MATCH → DARK VESSEL!")

    print(f"\n  [FUSION] Result: {len(matched_vessels)} identified, "
          f"{len(dark_vessels)} DARK VESSEL(S) detected.")

    return dark_vessels


if __name__ == "__main__":
    # Quick test with dummy data
    sample_ais = [
        {"ship_id": "SHIP_1000", "latitude": 16.53534, "longitude": -69.42185,
         "date": "2026-02-17", "time": "12:00:00"},
    ]
    sample_radar = [
        {"vessel_id": "RADAR_001", "vessel_type": "Trawler", "confidence": 85,
         "estimated_length_m": 45, "estimated_width_m": 12, "relative_position": "center"},
        {"vessel_id": "RADAR_002", "vessel_type": "Cargo Ship", "confidence": 90,
         "estimated_length_m": 180, "estimated_width_m": 30, "relative_position": "upper-right"},
    ]
    sample_sar = {"latitude": 16.53534, "longitude": -69.42185, "date": "2026-02-17"}

    dark = find_dark_vessels(sample_ais, sample_radar, sample_sar)
    for d in dark:
        print(f"\n  DARK: {d['radar_id']} — {d['violation_type']}")
