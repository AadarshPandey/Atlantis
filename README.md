### GMIE Project Directory Structure

```text
GMIE_Project/
├── app.py                # The main 'brain' that starts the whole system.
├── requirements.txt      # A list of all the Python tools (libraries) to install.
├── config/
│   └── settings.py       # Stores your API keys and the GPS coordinates of the zones you monitor.
├── src/
│   ├── ingestion/
│   │   ├── ais_stream.py # Connects to AIS feeds to collect ship ID signals.
│   │   └── sar_fetch.py  # Automatically downloads radar images from the satellite database.
│   ├── ai_models/
│   │   ├── detector.py   # The AI code that finds white dots (ships) in the radar images.
│   │   └── fusion.py     # The logic that compares Radar dots vs. AIS signals to find 'Dark Vessels'.
│   ├── forensics/
│   │   ├── hasher.py     # Creates the unique digital fingerprint for the evidence.
│   │   └── timestamp.py  # Connects to the Timestamp Authority for the legal 'time-seal'.
│   └── reporting/
│       └── pdf_gen.py    # Converts all the proof into a professional Evidence-Grade PDF.
├── data/                 # A folder to store the satellite images and ship logs temporarily.
└── reports/              # The final folder where the completed legal PDFs are saved.

```

---

Would you like me to generate the **`requirements.txt`** file with the exact versions of the libraries needed to run this stack?