# The main 'brain' that starts the whole GMIE system.
# Orchestrates the full Dark Vessel Detection pipeline.

import sys
from pathlib import Path

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import GEMINI_API_KEY, REPORTS_DIR
from src.ingestion.ais_stream import get_ais_data
from src.ingestion.sar_fetch import fetch_sar_image
from src.ai_models.detector import detect_vessels
from src.ai_models.fusion import find_dark_vessels
from src.forensics.hasher import hash_evidence
from src.forensics.timestamp import get_ist_timestamp
from src.reporting.pdf_gen import generate_report


def run_pipeline():
    """Execute the full GMIE Dark Vessel Detection pipeline."""

    print("=" * 70)
    print("  GMIE — Global Maritime Intelligence Engine")
    print("  Dark Vessel Detection Pipeline")
    print("=" * 70)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: Collecting the Evidence (The "Stakeout")
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n▶ STEP 1: Collecting Evidence (The 'Stakeout')")
    print("─" * 50)

    # 1a. Fetch SAR satellite image
    print("\n  📡 Fetching SAR satellite image...")
    sar_metadata = fetch_sar_image()

    # 1b. Collect AIS signals from the area
    print("\n  📻 Collecting AIS ship signals...")
    ais_data = get_ais_data()

    print(f"\n  ✅ Stakeout complete: 1 SAR image + {len(ais_data)} AIS pings collected.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: The AI Check (The "Identification")
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n▶ STEP 2: AI Vessel Detection (The 'Identification')")
    print("─" * 50)

    # Check if Gemini API key is configured
    if GEMINI_API_KEY == "your_gemini_api_key_here":
        print("\n  ⚠️  WARNING: Gemini API key not configured in .env file!")
        print("     Set GEMINI_API_KEY in .env to enable AI vessel detection.")
        print("     Using fallback detection for demonstration...\n")

    radar_detections = detect_vessels(sar_metadata["image_path"])

    print(f"\n  ✅ AI scan complete: {len(radar_detections)} vessel(s) detected by radar.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: Fusion — Finding Dark Vessels
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n▶ STEP 3: Data Fusion (Radar vs. AIS Comparison)")
    print("─" * 50)

    dark_vessels = find_dark_vessels(ais_data, radar_detections, sar_metadata)

    if dark_vessels:
        print(f"\n  🚨 ALERT: {len(dark_vessels)} DARK VESSEL(S) DETECTED!")
    else:
        print(f"\n  ✅ No dark vessels found — all ships are broadcasting AIS.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: Creating the "Legal Lock" (The "Proof")
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n▶ STEP 4: Forensic Evidence Hashing (The 'Legal Lock')")
    print("─" * 50)

    hash_result = hash_evidence(
        image_path=sar_metadata["image_path"],
        detection_results=radar_detections,
        dark_vessels=dark_vessels,
    )

    print(f"\n  🔒 Evidence sealed with SHA-256 hash.")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 5: Timestamp from the Internet (IST)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n▶ STEP 5: Legal Timestamp (RFC 3161 Time-Seal)")
    print("─" * 50)

    timestamp_result = get_ist_timestamp()

    print(f"\n  ⏱️  Timestamp verified: {timestamp_result['datetime_ist']} IST")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 6: Filing the Report (The "Incident Paperwork")
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n▶ STEP 6: Generating Forensic Report (The 'Incident Paperwork')")
    print("─" * 50)

    report_path = generate_report(
        sar_metadata=sar_metadata,
        ais_data=ais_data,
        radar_detections=radar_detections,
        dark_vessels=dark_vessels,
        hash_result=hash_result,
        timestamp_result=timestamp_result,
    )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # DONE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "=" * 70)
    print("  ✅ PIPELINE COMPLETE")
    print(f"  📄 Report saved to: {report_path}")
    if dark_vessels:
        print(f"  🚨 {len(dark_vessels)} Dark Vessel(s) documented for enforcement.")
    else:
        print(f"  ✅ Zone is compliant — no violations found.")
    print("=" * 70)

    return report_path


if __name__ == "__main__":
    run_pipeline()
