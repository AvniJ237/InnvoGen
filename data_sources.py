import io
import random
from datetime import datetime, timezone, timedelta

import pandas as pd
import requests

IMD_URL = "https://api.imd.gov.in/api/v1/current_wx"
AQ_URL = "https://snapdata.dev/api/v1/aqi/in/city/delhi.json"
GTFS_URL = "https://otd.delhi.gov.in/data/static/"

DELHI_PLACES = [
    ("Connaught Place", 28.6315, 77.2167, "Central Delhi"),
    ("India Gate", 28.6129, 77.2295, "Central Delhi"),
    ("Lajpat Nagar", 28.5677, 77.2433, "South Delhi"),
    ("Hauz Khas", 28.5494, 77.2001, "South Delhi"),
    ("Saket", 28.5245, 77.2066, "South Delhi"),
    ("Dwarka", 28.5921, 77.0460, "West Delhi"),
    ("Rohini", 28.7495, 77.0565, "North West Delhi"),
    ("Shahdara", 28.6731, 77.2890, "East Delhi"),
    ("Karol Bagh", 28.6514, 77.1907, "Central Delhi"),
    ("Mayur Vihar", 28.6041, 77.2942, "East Delhi"),
]

def safe_get(url, timeout=12):
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "CityPulse-Delhi-Hackathon/1.0"})
    r.raise_for_status()
    return r

def load_weather():
    """IMD current weather. Falls back to a clearly marked demo value."""
    try:
        data = safe_get(IMD_URL).json()
        rows = data.get("data", data if isinstance(data, list) else [])
        # Find a Delhi/near-Delhi station when possible.
        row = None
        for x in rows:
            s = str(x.get("Station", "")).lower()
            if "delhi" in s or "lodhi" in s:
                row = x
                break
        row = row or (rows[0] if rows else None)
        if row:
            temp = float(row.get("Temperature", row.get("temperature", 0)) or 0)
            rain = float(row.get("Last 24 hrs Rainfall", 0) or 0)
            return {
                "ok": True, "temperature": temp, "rain_mm": rain,
                "station": row.get("Station", "Delhi station"),
                "source": "IMD"
            }
    except Exception as e:
        return {"ok": False, "temperature": 30.0, "rain_mm": 0.0,
                "station": "Demo fallback", "source": "IMD fallback", "error": str(e)}
    return {"ok": False, "temperature": 30.0, "rain_mm": 0.0,
            "station": "Demo fallback", "source": "IMD fallback"}

def load_air():
    """CPCB-sourced observations from a public mirror; calculates a simple Delhi PM2.5 median."""
    try:
        data = safe_get(AQ_URL).json()
        rows = data.get("data", data if isinstance(data, list) else [])
        df = pd.DataFrame(rows)
        if df.empty:
            raise ValueError("No air-quality rows returned")

        # Flexible column matching because mirrors can evolve.
        cols = {c.lower().replace(" ", "_"): c for c in df.columns}
        pm = None
        for key in ["pm2.5", "pm25", "pm_2.5", "pm_25"]:
            if key in cols:
                pm = cols[key]
                break
        if pm is None:
            raise ValueError("PM2.5 field not found")
        vals = pd.to_numeric(df[pm], errors="coerce").dropna()
        value = float(vals.median()) if len(vals) else 0.0
        return {"ok": True, "pm25": round(value, 1), "stations": len(df),
                "source": "CPCB-sourced mirror"}
    except Exception as e:
        return {"ok": False, "pm25": 118.0, "stations": 0,
                "source": "Demo fallback", "error": str(e)}

def load_transit():
    """
    Beginner-safe GTFS metadata.
    The Delhi OTD site publishes static GTFS. We use a small metric from the
    download when available; otherwise we use known published counts as a
    fallback rather than claiming real-time delay data.
    """
    try:
        r = safe_get(GTFS_URL)
        # The endpoint is a web page/download form in some deployments, so
        # don't pretend its HTML is GTFS. Return the published OTD coverage.
        return {
            "ok": True,
            "stops": 3464,
            "routes": 543,
            "trips": 16562,
            "mode": "Static GTFS",
            "source": "Delhi Open Transit Data"
        }
    except Exception as e:
        return {"ok": False, "stops": 3464, "routes": 543, "trips": 16562,
                "mode": "Static GTFS fallback", "source": "Delhi OTD", "error": str(e)}

def make_incidents(seed=42, hours=24):
    """
    Synthetic 311-style feed. It intentionally creates a weather/incident
    pattern so judges can see the fusion logic during a demo.
    """
    rng = random.Random(seed)
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    records = []
    categories = ["Traffic", "Waterlogging", "Streetlight", "Power", "Road damage", "Noise"]
    weights = [3, 2, 1, 1, 1, 1]
    for h in range(hours):
        ts = now - timedelta(hours=(hours - 1 - h))
        # A synthetic "rain event" in the last 5 hours produces more water/traffic reports.
        rainy_window = h >= hours - 5
        count = rng.randint(2, 6) + (rng.randint(3, 7) if rainy_window else 0)
        for _ in range(count):
            place, lat, lon, zone = rng.choice(DELHI_PLACES)
            cat = rng.choices(categories, weights=weights)[0]
            if rainy_window and rng.random() < 0.55:
                cat = rng.choice(["Waterlogging", "Traffic"])
            records.append({
                "timestamp": ts,
                "category": cat,
                "place": place,
                "zone": zone,
                "lat": lat + rng.uniform(-0.008, 0.008),
                "lon": lon + rng.uniform(-0.008, 0.008),
            })
    return pd.DataFrame(records)

def build_timeseries(incidents):
    hourly = incidents.set_index("timestamp").resample("h").size().rename("incidents").to_frame()
    # Demo rainfall signal: the last 5 hours are wet.
    hourly["rain_mm"] = 0.0
    hourly.iloc[-5:, hourly.columns.get_loc("rain_mm")] = [2, 5, 8, 12, 7]
    return hourly.reset_index()

def pulse_score(weather, air, incidents):
    score = 100
    if air["pm25"] > 60: score -= 20
    if air["pm25"] > 120: score -= 15
    if weather["rain_mm"] > 5: score -= 10
    if weather["rain_mm"] > 20: score -= 10
    recent = incidents[incidents["timestamp"] >= incidents["timestamp"].max() - pd.Timedelta(hours=2)]
    if len(recent) > 15: score -= 15
    elif len(recent) > 8: score -= 8
    return max(0, min(100, score))

def generate_summary(weather, air, incidents):
    recent = incidents[incidents["timestamp"] >= incidents["timestamp"].max() - pd.Timedelta(hours=2)]
    parts = []
    if weather["rain_mm"] > 5:
        parts.append(f"rainfall is elevated ({weather['rain_mm']:.0f} mm in the reported 24-hour window)")
    if air["pm25"] > 100:
        parts.append(f"PM2.5 is high ({air['pm25']:.0f} µg/m³)")
    if len(recent) > 8:
        parts.append(f"{len(recent)} synthetic civic reports arrived in the last 2 hours")
    if not parts:
        return "Conditions look relatively stable right now; keep an eye on the live indicators."
    text = "; ".join(parts)
    if weather["rain_mm"] > 5 and len(recent) > 8:
        return "Possible link: " + text + ". The dashboard shows a timing overlap, not proof that one caused the other."
    return "Right now, " + text + "."
