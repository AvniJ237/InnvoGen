# CityPulse Delhi — beginner-friendly civic health dashboard

A 24-hour hackathon MVP that fuses:
1. IMD Delhi weather/current conditions
2. CPCB-sourced Delhi air-quality observations via a public mirror
3. Delhi Open Transit Data static GTFS
4. Synthetic civic incidents/311-style reports (used because a public live 311 API is not assumed)

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints, usually http://localhost:8501.

## Important data notes

- IMD is used for weather. The app calls the public IMD API.
- Air-quality data is CPCB-sourced through a public mirror so the beginner MVP does not require a CPCB API key.
- Delhi Open Transit Data provides static GTFS. Its real-time vehicle API requires an access key, so this MVP uses the static feed and calculates a "transit coverage" metric rather than pretending it has live delays.
- Incidents are synthetic and clearly labeled. They are generated around real Delhi places only to demonstrate the fusion/correlation workflow.
- Correlation language is deliberately cautious: "possible link", not "cause".

## Recommended hackathon demo

1. Start the app.
2. Select South Delhi / Central Delhi.
3. Turn on/off Weather, Air Quality, Transit and Incidents.
4. Click Refresh data.
5. Explain the "What’s happening?" card.
6. Open the Correlation section and show how rainfall + incidents are compared over time.

## If you later get Delhi transit real-time access

Replace `load_transit()` in `data_sources.py` with calls to:
`https://otd.delhi.gov.in/api/realtime/VehiclePositions.pb?key=YOUR_PRIVATE_KEY`

Do not commit the key to GitHub. Use Streamlit secrets instead.
