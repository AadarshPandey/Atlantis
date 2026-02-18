# The AI code that finds white dots (ships) in the radar images.
# Uses Google Gemini Vision API to detect vessels in SAR satellite imagery.

import json
import random
from pathlib import Path


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


# ── Vision-capable Gemini models ─────────────────────────────────────────────
VISION_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-pro-preview-05-06",
]


def fallback_detections() -> list[dict]:
    """Return sample detections when the Gemini API is unavailable."""
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


def detect_vessels(image_path: str, api_key: str = None,
                   model_name: str = "gemini-2.0-flash") -> list[dict]:
    """
    Send a SAR image to Gemini Vision API and ask it to identify ships.

    Args:
        image_path:  Path to the SAR satellite image.
        api_key:     Gemini API key. If None/empty, uses fallback detections.
        model_name:  Gemini model to use (must support vision).

    Returns:
        List of detected vessel dicts.
    """
    # ── Check if API key is provided ─────────────────────────────────────────
    if not api_key or api_key == "your_gemini_api_key_here":
        print("  [AI] No valid Gemini API key — using fallback detections.")
        detections = fallback_detections()
        for d in detections:
            print(f"       → {d['vessel_id']}: {d['vessel_type']} "
                  f"({d['confidence']}% confidence)")
        return detections

    # ── Call Gemini API ──────────────────────────────────────────────────────
    print(f"  [AI] Sending SAR image to Gemini ({model_name}) for vessel detection...")

    try:
        from google import genai
        from google.genai.types import Part

        client = genai.Client(api_key=api_key)

        # Read image bytes
        image_bytes = Path(image_path).read_bytes()

        response = client.models.generate_content(
            model=model_name,
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
        return fallback_detections()

    except Exception as e:
        print(f"  [AI] ERROR: Gemini API call failed: {e}")
        raise


if __name__ == "__main__":
    import sys as _sys
    sys_path = str(Path(__file__).resolve().parent.parent.parent)
    _sys.path.insert(0, sys_path)

    if len(_sys.argv) > 1:
        results = detect_vessels(_sys.argv[1])
    else:
        from src.ingestion.sar_fetch import fetch_sar_image
        sar = fetch_sar_image()
        results = detect_vessels(sar["image_path"])

    print(f"\nDetection results: {json.dumps(results, indent=2)}")
