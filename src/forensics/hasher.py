# Creates the unique digital fingerprint for the evidence.
# Uses SHA-256 hashing to ensure data integrity and tamper-proof evidence.

import hashlib
import json
from pathlib import Path


def hash_evidence(image_path: str, detection_results: list[dict],
                  dark_vessels: list[dict]) -> dict:
    """
    Create a SHA-256 hash of the combined evidence package.

    The hash covers:
      1. The raw bytes of the SAR satellite image
      2. The JSON-serialized detection results
      3. The JSON-serialized dark vessel findings

    This creates an immutable "digital fingerprint" — if even a single
    pixel or character is changed, the hash will be completely different.

    Args:
        image_path:        Path to the SAR image file.
        detection_results: List of radar detection dicts.
        dark_vessels:      List of dark vessel incident dicts.

    Returns:
        Dict with keys: evidence_hash, image_hash, data_hash, algorithm
    """
    hasher_full = hashlib.sha256()
    hasher_image = hashlib.sha256()
    hasher_data = hashlib.sha256()

    # ── Hash 1: Image bytes ──────────────────────────────────────────────────
    image_file = Path(image_path)
    if image_file.exists():
        image_bytes = image_file.read_bytes()
        hasher_image.update(image_bytes)
        hasher_full.update(image_bytes)
        print(f"  [HASH] Image hashed: {len(image_bytes):,} bytes")
    else:
        print(f"  [HASH] WARNING: Image not found at {image_path}")

    # ── Hash 2: Detection + Dark Vessel data ─────────────────────────────────
    evidence_json = json.dumps({
        "detections": detection_results,
        "dark_vessels": dark_vessels,
    }, sort_keys=True, default=str)
    data_bytes = evidence_json.encode("utf-8")
    hasher_data.update(data_bytes)
    hasher_full.update(data_bytes)

    image_hash = hasher_image.hexdigest()
    data_hash = hasher_data.hexdigest()
    full_hash = hasher_full.hexdigest()

    print(f"  [HASH] Evidence Hash (SHA-256): {full_hash[:16]}...{full_hash[-8:]}")

    return {
        "evidence_hash": full_hash,
        "image_hash": image_hash,
        "data_hash": data_hash,
        "algorithm": "SHA-256",
    }


if __name__ == "__main__":
    # Quick test
    result = hash_evidence(
        image_path="data/11.26284N_66.40861W_2026-02-20.jpeg",
        detection_results=[{"vessel_id": "RADAR_001", "type": "Trawler"}],
        dark_vessels=[{"radar_id": "RADAR_001", "ais_status": "NO SIGNAL"}],
    )
    print(f"\n  Full hash: {result['evidence_hash']}")
