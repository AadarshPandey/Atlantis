# Automatically downloads radar images from the satellite database.
# For demonstration: picks a random SAR image from the local data/ folder.

import random
import re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import DATA_DIR


def _parse_filename(filename: str) -> dict | None:
    """
    Parse a SAR image filename to extract metadata.
    Expected format: [Lat][N/S]_[Lon][E/W]_[Date].jpeg
    Example:         11.26284N_66.40861W_2026-02-20.jpeg
    """
    pattern = r"^([\d.]+)([NS])_([\d.]+)([EW])_(\d{4}-\d{2}-\d{2})\.jpeg$"
    match = re.match(pattern, filename)
    if not match:
        return None

    lat = float(match.group(1))
    lat_dir = match.group(2)
    lon = float(match.group(3))
    lon_dir = match.group(4)
    date = match.group(5)

    # Convert to signed coordinates (S = negative lat, W = negative lon)
    if lat_dir == "S":
        lat = -lat
    if lon_dir == "W":
        lon = -lon

    return {
        "latitude": lat,
        "longitude": lon,
        "lat_direction": lat_dir,
        "lon_direction": lon_dir,
        "date": date,
    }


def fetch_sar_image() -> dict:
    """
    Simulate fetching a SAR image by randomly selecting one from data/.

    Returns:
        Dict with keys: image_path, latitude, longitude, date, image_id
    """
    images = list(DATA_DIR.glob("*.jpeg"))
    if not images:
        raise FileNotFoundError(f"No .jpeg images found in {DATA_DIR}")

    selected = random.choice(images)
    metadata = _parse_filename(selected.name)

    if metadata is None:
        raise ValueError(f"Could not parse filename: {selected.name}")

    result = {
        "image_path": str(selected),
        "image_name": selected.name,
        "latitude": metadata["latitude"],
        "longitude": metadata["longitude"],
        "lat_direction": metadata["lat_direction"],
        "lon_direction": metadata["lon_direction"],
        "date": metadata["date"],
        "image_id": f"S1-{selected.stem.replace('.', '').replace('_', '-')}",
    }

    print(f"  [SAR] Selected image: {selected.name}")
    print(f"        Location: {abs(result['latitude'])}°{metadata['lat_direction']}, "
          f"{abs(result['longitude'])}°{metadata['lon_direction']}")
    print(f"        Date: {result['date']}")

    return result


if __name__ == "__main__":
    img = fetch_sar_image()
    print(f"\n  Image path: {img['image_path']}")
    print(f"  Image ID:   {img['image_id']}")
