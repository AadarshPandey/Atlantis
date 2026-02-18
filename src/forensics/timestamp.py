# Connects to the Timestamp Authority for the legal 'time-seal'.
# Fetches current Indian Standard Time (IST) from the internet.

import requests
from datetime import datetime, timezone, timedelta


# IST is UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))


def get_ist_timestamp() -> dict:
    """
    Fetch the current Indian Standard Time from worldtimeapi.org.

    Falls back to the local system clock if the API is unreachable.

    Returns:
        Dict with keys: datetime_ist, datetime_utc, source, timezone
    """
    print("  [TIME] Fetching IST timestamp from worldtimeapi.org...")

    try:
        response = requests.get(
            "http://worldtimeapi.org/api/timezone/Asia/Kolkata",
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Parse the datetime string from the API
        raw_dt = data.get("datetime", "")
        # The API returns format like: 2026-02-18T23:05:23.123456+05:30
        ist_dt = datetime.fromisoformat(raw_dt)
        utc_dt = ist_dt.astimezone(timezone.utc)

        source = "worldtimeapi.org (Internet)"
        print(f"  [TIME] IST: {ist_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    except Exception as e:
        print(f"  [TIME] API unavailable ({e}), falling back to system clock.")
        utc_dt = datetime.now(timezone.utc)
        ist_dt = utc_dt.astimezone(IST)
        source = "System Clock (Fallback)"
        print(f"  [TIME] IST (system): {ist_dt.strftime('%Y-%m-%d %H:%M:%S')}")

    return {
        "datetime_ist": ist_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "datetime_utc": utc_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "timezone": "Asia/Kolkata (IST, UTC+05:30)",
    }


if __name__ == "__main__":
    ts = get_ist_timestamp()
    print(f"\n  IST: {ts['datetime_ist']}")
    print(f"  UTC: {ts['datetime_utc']}")
    print(f"  Source: {ts['source']}")
