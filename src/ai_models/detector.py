# The AI code that finds white dots (ships) in the radar images.
# Uses Google Gemini Vision API to detect vessels in SAR satellite imagery.

import json
import base64
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config.settings import GEMINI_API_KEY


# ── Gemini Vision Prompt ─────────────────────────────────────────────────────
_DETECTION_PROMPT = """You are a maritime radar analyst. Analyze this SAR (Synthetic Aperture Radar) 
satellite image of the ocean. Look for bright white dots or shapes that indicate the 
presence of metal vessels (ships/boats) on the water surface.

For each vessel you detect, provide the following information in a JSON array:
- vessel_id: A unique label like "RADAR_001", "RADAR_002", etc.
- vessel_type: Your best guess (e.g., "Industrial Trawler", "Cargo Ship", "Tanker", "Fishing Boat", "Unknown Vessel")
- estimated_length_m: Estimated length in meters (integer)
- estimated_width_m: Estimated width in meters (integer)
- confidence: Detection confidence as a percentage (integer, 0-100)
- relative_position: A brief description of where in the image the vessel appears (e.g., "center-left", "upper-right")

IMPORTANT: Return ONLY a valid JSON array. No markdown formatting, no code fences, no explanation.
If no vessels are detected, return an empty array: []

Example output:
[{"vessel_id": "RADAR_001", "vessel_type": "Cargo Ship", "estimated_length_m": 180, "estimated_width_m": 30, "confidence": 85, "relative_position": "center-left"}]"""


def _fallback_detections() -> list[dict]:
    """Return sample detections when the Gemini API is unavailable."""
    import random
    vessel_types = ["Industrial Trawler", "Cargo Ship", "Fishing Boat", "Tanker", "Unknown Vessel"]
    positions = ["center-left", "upper-right", "lower-center", "center", "upper-left"]
    num = random.randint(2, 5)

    detections = []
    for i in range(num):
        detections.append({
            "vessel_id": f"RADAR_{i + 1:03d}",
            "vessel_type": random.choice(vessel_types),
            "estimated_length_m": random.randint(20, 250),
            "estimated_width_m": random.randint(5, 40),
            "confidence": random.randint(60, 98),
            "relative_position": random.choice(positions),
        })
    return detections


def detect_vessels(image_path: str) -> list[dict]:
    """
    Send a SAR image to Gemini Vision API and ask it to identify ships.

    If the API key is invalid or the API is unreachable, falls back to
    simulated detections for demonstration purposes.

    Args:
        image_path: Path to the SAR satellite image.

    Returns:
        List of detected vessel dicts with keys:
            vessel_id, vessel_type, estimated_length_m,
            estimated_width_m, confidence, relative_position
    """
    # ── Check if API key looks valid ─────────────────────────────────────────
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("  [AI] No valid Gemini API key — using fallback detections.")
        detections = _fallback_detections()
        for d in detections:
            print(f"       → {d['vessel_id']}: {d['vessel_type']} "
                  f"({d['confidence']}% confidence)")
        return detections

    # ── Call Gemini API ──────────────────────────────────────────────────────
    print(f"  [AI] Sending SAR image to Gemini for vessel detection...")

    try:
        from google import genai
        from google.genai.types import Part

        client = genai.Client(api_key=GEMINI_API_KEY)

        # Read image bytes
        image_bytes = Path(image_path).read_bytes()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                _DETECTION_PROMPT,
                Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            ],
        )

        response_text = response.text.strip()

        # Clean up response — remove markdown fences if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        detections = json.loads(response_text)

        if not isinstance(detections, list):
            detections = [detections]

        print(f"  [AI] Detected {len(detections)} vessel(s) in the image.")
        for d in detections:
            print(f"       → {d.get('vessel_id', '?')}: {d.get('vessel_type', '?')} "
                  f"({d.get('confidence', '?')}% confidence)")

        return detections

    except json.JSONDecodeError as e:
        print(f"  [AI] WARNING: Could not parse Gemini response as JSON: {e}")
        print(f"       Falling back to simulated detections.")
        return _fallback_detections()

    except Exception as e:
        print(f"  [AI] ERROR: Gemini API call failed: {e}")
        print(f"       Falling back to simulated detections.")
        return _fallback_detections()


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1:
        results = detect_vessels(_sys.argv[1])
    else:
        from src.ingestion.sar_fetch import fetch_sar_image
        sar = fetch_sar_image()
        results = detect_vessels(sar["image_path"])

    print(f"\nDetection results: {json.dumps(results, indent=2)}")
