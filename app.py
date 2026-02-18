# ══════════════════════════════════════════════════════════════════════════════
# GMIE — Global Maritime Intelligence Engine
# Streamlit Frontend for Dark Vessel Detection Pipeline
# Run:  streamlit run app.py
# ══════════════════════════════════════════════════════════════════════════════

import sys
import time
from pathlib import Path

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from config.settings import REPORTS_DIR, DATA_DIR
from src.ingestion.ais_stream import get_ais_data
from src.ingestion.sar_fetch import fetch_sar_image
from src.ai_models.detector import detect_vessels, fallback_detections, VISION_MODELS
from src.ai_models.fusion import find_dark_vessels
from src.forensics.hasher import hash_evidence
from src.forensics.timestamp import get_ist_timestamp
from src.reporting.pdf_gen import generate_report

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GMIE — Dark Vessel Detection",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global font */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Dark gradient header */
    .main-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #a0aec0;
        font-size: 1rem;
        margin: 0.4rem 0 0 0;
    }

    /* Step cards */
    .step-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #e94560;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .step-card h3 {
        color: #e94560;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    .step-card p {
        color: #cbd5e0;
        margin: 0;
        font-size: 0.9rem;
    }

    /* Alert banner */
    .dark-vessel-alert {
        background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1.5rem 0;
        animation: pulse-glow 2s ease-in-out infinite alternate;
    }
    .dark-vessel-alert h2 {
        color: white;
        margin: 0;
        font-size: 1.4rem;
        font-weight: 800;
    }
    .dark-vessel-alert p {
        color: #fecaca;
        margin: 0.3rem 0 0 0;
    }

    @keyframes pulse-glow {
        from { box-shadow: 0 0 10px rgba(220,38,38,0.4); }
        to   { box-shadow: 0 0 25px rgba(220,38,38,0.8); }
    }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #60a5fa;
    }
    .stat-card .stat-label {
        font-size: 0.78rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li {
        color: #94a3b8;
    }

    /* Vessel table */
    .vessel-row {
        background: rgba(15, 23, 42, 0.6);
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #f59e0b;
    }
    .vessel-row.dark {
        border-left: 3px solid #ef4444;
        background: rgba(127, 29, 29, 0.2);
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fix expander overlap */
    .streamlit-expanderHeader, 
    [data-testid="stExpander"] summary {
        position: relative;
        z-index: 1;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.5;
        overflow: visible;
    }
    [data-testid="stExpander"] summary span {
        display: inline;
        white-space: normal;
        overflow: visible;
        text-overflow: unset;
    }
    [data-testid="stExpander"] {
        overflow: visible;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Configuration
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    # API Key input
    st.markdown("### 🔑 Gemini API Key")
    api_key = st.text_input(
        "Enter your Google Gemini API key",
        type="password",
        placeholder="AIzaSy...",
        help="Get a free key from [Google AI Studio](https://aistudio.google.com/apikey)",
    )

    if api_key:
        st.success("API key provided ✓", icon="✅")
    else:
        st.warning("No API key — pipeline will use simulated detections", icon="⚠️")

    st.markdown("---")

    # Model selector
    st.markdown("### 🤖 Vision Model")
    selected_model = st.selectbox(
        "Select Gemini model",
        options=VISION_MODELS,
        index=0,
        help="All listed models support image analysis. Flash models are faster; Pro models are more accurate.",
    )

    st.markdown("---")

    # Image selector
    st.markdown("### 🛰️ SAR Image")
    available_images = sorted(DATA_DIR.glob("*.jpeg"))
    image_names = [img.name for img in available_images]

    image_mode = st.radio(
        "Image selection",
        ["Random", "Choose specific image"],
        index=0,
    )

    selected_image_path = None
    if image_mode == "Choose specific image" and image_names:
        chosen = st.selectbox("Select image", image_names)
        selected_image_path = str(DATA_DIR / chosen)

    st.markdown("---")

    # Info
    st.markdown("### 📖 About")
    st.markdown(
        "**GMIE** detects *dark vessels* — ships that disable AIS transponders "
        "to operate illegally. It fuses SAR radar imagery with AIS data and "
        "generates forensic reports."
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA — Header
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
    <h1>🛰️ GMIE — Global Maritime Intelligence Engine</h1>
    <p>AI-Powered Dark Vessel Detection & Forensic Evidence Pipeline</p>
</div>
""", unsafe_allow_html=True)


# ── Launch button ────────────────────────────────────────────────────────────
col_btn, col_info = st.columns([1, 3])
with col_btn:
    run_pipeline = st.button("🚀 **Run Detection Pipeline**", width="stretch", type="primary")
with col_info:
    st.caption(
        f"Model: **{selected_model}** · "
        f"API Key: {'✅ Set' if api_key else '❌ Not set (fallback mode)'} · "
        f"Images: {len(image_names)} available"
    )


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE EXECUTION
# ══════════════════════════════════════════════════════════════════════════════
if run_pipeline:
    st.markdown("---")

    # ━━━━━━━ STEP 1: Evidence Collection ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("""<div class="step-card">
        <h3>▶ STEP 1 — Collecting Evidence (The "Stakeout")</h3>
        <p>Fetching SAR satellite image and AIS ship signals from the monitoring zone.</p>
    </div>""", unsafe_allow_html=True)

    with st.spinner("📡 Fetching SAR image & AIS signals..."):
        # SAR image
        if selected_image_path:
            from src.ingestion.sar_fetch import _parse_filename
            img_path = Path(selected_image_path)
            meta = _parse_filename(img_path.name)
            sar_metadata = {
                "image_path": str(img_path),
                "image_name": img_path.name,
                "latitude": meta["latitude"],
                "longitude": meta["longitude"],
                "lat_direction": meta["lat_direction"],
                "lon_direction": meta["lon_direction"],
                "date": meta["date"],
                "image_id": f"S1-{img_path.stem.replace('.', '').replace('_', '-')}",
            }
        else:
            sar_metadata = fetch_sar_image()

        # AIS data
        ais_data = get_ais_data()

    col1, col2 = st.columns(2)
    with col1:
        st.image(sar_metadata["image_path"], caption=f"SAR Image: {sar_metadata['image_name']}", width="stretch")
    with col2:
        st.markdown("**📡 SAR Metadata**")
        st.json({
            "Image ID": sar_metadata["image_id"],
            "Location": f"{abs(sar_metadata['latitude']):.5f}°{sar_metadata.get('lat_direction', 'N')}, "
                        f"{abs(sar_metadata['longitude']):.5f}°{sar_metadata.get('lon_direction', 'W')}",
            "Date": sar_metadata["date"],
        })

        st.markdown("**📻 AIS Signals**")
        import pandas as pd
        ais_df = pd.DataFrame(ais_data)
        st.dataframe(ais_df, width="stretch", hide_index=True)

    st.success(f"✅ Stakeout complete: 1 SAR image + {len(ais_data)} AIS pings collected.")

    # ━━━━━━━ STEP 2: AI Detection ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("""<div class="step-card">
        <h3>▶ STEP 2 — AI Vessel Detection (The "Identification")</h3>
        <p>Analyzing SAR imagery with Gemini Vision AI to identify vessels.</p>
    </div>""", unsafe_allow_html=True)

    with st.spinner(f"🤖 Analyzing image with {selected_model}..."):
        try:
            radar_detections = detect_vessels(
                sar_metadata["image_path"],
                api_key=api_key if api_key else None,
                model_name=selected_model,
            )
            detection_source = "Gemini AI" if api_key else "Simulated (No API Key)"
        except Exception as e:
            st.error(f"❌ Gemini API error: {e}")
            st.info("Falling back to simulated detections.")
            radar_detections = fallback_detections()
            detection_source = "Simulated (API Error)"

    st.markdown(f"**Detection Source:** `{detection_source}`")

    det_df = pd.DataFrame(radar_detections)
    st.dataframe(det_df, width="stretch", hide_index=True)
    st.success(f"✅ Detected {len(radar_detections)} vessel(s) in the SAR image.")

    # ━━━━━━━ STEP 3: Fusion ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("""<div class="step-card">
        <h3>▶ STEP 3 — Data Fusion (Radar vs. AIS Comparison)</h3>
        <p>Comparing radar detections against AIS signals to identify dark vessels.</p>
    </div>""", unsafe_allow_html=True)

    with st.spinner("⚡ Running fusion analysis..."):
        dark_vessels = find_dark_vessels(ais_data, radar_detections, sar_metadata)

    # Show results
    if dark_vessels:
        st.markdown(f"""<div class="dark-vessel-alert">
            <h2>🚨 {len(dark_vessels)} DARK VESSEL(S) DETECTED</h2>
            <p>Ships detected on radar with NO matching AIS signal — potential illegal activity.</p>
        </div>""", unsafe_allow_html=True)

        dark_df = pd.DataFrame([{
            "Radar ID": dv["radar_id"],
            "Type": dv["vessel_type"],
            "Length (m)": dv["estimated_length_m"],
            "Width (m)": dv["estimated_width_m"],
            "Confidence": f"{dv['confidence']}%",
            "AIS Status": dv["ais_status"],
        } for dv in dark_vessels])
        st.dataframe(dark_df, width="stretch", hide_index=True)
    else:
        st.success("✅ No dark vessels found — all ships are broadcasting AIS.")

    # ━━━━━━━ STEP 4: Forensic Hashing ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("""<div class="step-card">
        <h3>▶ STEP 4 — Forensic Evidence Hashing (The "Legal Lock")</h3>
        <p>Creating an immutable SHA-256 fingerprint of all evidence.</p>
    </div>""", unsafe_allow_html=True)

    with st.spinner("🔐 Hashing evidence..."):
        hash_result = hash_evidence(
            image_path=sar_metadata["image_path"],
            detection_results=radar_detections,
            dark_vessels=dark_vessels,
        )

    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Evidence Hash</div>
            <div style="color:#60a5fa;font-size:0.7rem;word-break:break-all;font-family:monospace;margin-top:0.5rem;">
                {hash_result['evidence_hash']}
            </div>
        </div>""", unsafe_allow_html=True)
    with col_h2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Image Hash</div>
            <div style="color:#34d399;font-size:0.7rem;word-break:break-all;font-family:monospace;margin-top:0.5rem;">
                {hash_result['image_hash']}
            </div>
        </div>""", unsafe_allow_html=True)
    with col_h3:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Algorithm</div>
            <div class="stat-value">{hash_result['algorithm']}</div>
        </div>""", unsafe_allow_html=True)

    st.success("✅ Evidence sealed — tamper-proof hash generated.")

    # ━━━━━━━ STEP 5: Timestamp ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("""<div class="step-card">
        <h3>▶ STEP 5 — Legal Timestamp (RFC 3161 Time-Seal)</h3>
        <p>Fetching verified Indian Standard Time for the evidence chain.</p>
    </div>""", unsafe_allow_html=True)

    with st.spinner("⏱️ Fetching IST timestamp..."):
        timestamp_result = get_ist_timestamp()

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">IST Time</div>
            <div class="stat-value" style="font-size:1.2rem;">{timestamp_result['datetime_ist']}</div>
        </div>""", unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">UTC Time</div>
            <div class="stat-value" style="font-size:1.2rem;">{timestamp_result['datetime_utc']}</div>
        </div>""", unsafe_allow_html=True)
    with col_t3:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-label">Source</div>
            <div style="color:#a78bfa;font-size:0.85rem;margin-top:0.7rem;">{timestamp_result['source']}</div>
        </div>""", unsafe_allow_html=True)

    st.success("✅ Timestamp verified and sealed.")

    # ━━━━━━━ STEP 6: Report Generation ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("""<div class="step-card">
        <h3>▶ STEP 6 — Generating Forensic Report (The "Incident Paperwork")</h3>
        <p>Creating a court-admissible Markdown incident report.</p>
    </div>""", unsafe_allow_html=True)

    with st.spinner("📋 Generating forensic report..."):
        report_path = generate_report(
            sar_metadata=sar_metadata,
            ais_data=ais_data,
            radar_detections=radar_detections,
            dark_vessels=dark_vessels,
            hash_result=hash_result,
            timestamp_result=timestamp_result,
        )

    st.success(f"✅ Report saved to: `{report_path}`")

    # ━━━━━━━ RESULTS SUMMARY ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("---")
    st.markdown("## 📊 Pipeline Summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-value">{len(radar_detections)}</div>
            <div class="stat-label">Vessels Detected</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-value" style="color:#ef4444;">{len(dark_vessels)}</div>
            <div class="stat-label">Dark Vessels</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-value">{len(ais_data)}</div>
            <div class="stat-label">AIS Pings</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        avg_conf = sum(d.get("confidence", 0) for d in radar_detections) // max(len(radar_detections), 1)
        st.markdown(f"""<div class="stat-card">
            <div class="stat-value" style="color:#34d399;">{avg_conf}%</div>
            <div class="stat-label">Avg Confidence</div>
        </div>""", unsafe_allow_html=True)

    # ── Show report content ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## 📄 Generated Report")

    report_content = Path(report_path).read_text(encoding="utf-8")

    with st.expander("📋 View Full Forensic Report", expanded=True):
        st.code(report_content, language="markdown")

    # Download button
    st.download_button(
        label="📥 Download Report (.md)",
        data=report_content,
        file_name=Path(report_path).name,
        mime="text/markdown",
        type="primary",
    )

    # Pipeline completion banner
    if dark_vessels:
        st.markdown(f"""<div class="dark-vessel-alert">
            <h2>⚠️ PIPELINE COMPLETE — {len(dark_vessels)} VIOLATION(S) DOCUMENTED</h2>
            <p>Evidence sealed and report generated. Forward to port authority for enforcement.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.success("✅ Pipeline complete — zone is compliant, no violations found.")

# ── Footer when no pipeline is running ───────────────────────────────────────
else:
    st.markdown("---")

    st.markdown("### 🗺️ How It Works")

    cols = st.columns(3)
    steps = [
        ("1️⃣ Configure", "Set your Gemini API key and choose a vision model in the sidebar."),
        ("2️⃣ Launch", "Click **Run Detection Pipeline** to start the 6-step analysis."),
        ("3️⃣ Report", "Review the forensic report and download it for enforcement action."),
    ]
    for col, (title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""<div class="stat-card" style="text-align:left;padding:1.5rem;">
                <div style="font-size:1.3rem;font-weight:700;color:#e2e8f0;margin-bottom:0.5rem;">{title}</div>
                <div style="color:#94a3b8;font-size:0.9rem;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Show available images
    st.markdown("### 🖼️ Available SAR Images")
    img_cols = st.columns(min(len(available_images), 3)) if available_images else []
    for i, img_path in enumerate(available_images):
        with img_cols[i % len(img_cols)]:
            st.image(str(img_path), caption=img_path.name, width="stretch")
