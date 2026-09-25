import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from data_sources import (
    load_weather,
    load_air,
    load_transit,
    make_incidents,
    pulse_score,
)

st.html("""
    <style>
    /* Hide top header bar and toolbar */
    [data-testid="stHeader"] {
        display: none;
    }
    
    /* Remove unnecessary top whitespace */
    .main .block-container {
        padding-top: 1rem;
    }
    </style>
""")
# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="CityPulse Delhi",
    page_icon="💓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DESIGN
# =========================================================

st.markdown(
    """
    <style>
     [data-testid="stSidebarHeader"] {
            display: none; /* Hides default header spacing */
        }
        [data-testid="stSidebarUserContent"] {
            padding-top: 1rem !important;
        }


    /* ---------- PAGE ---------- */

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(125, 211, 252, 0.15),
                transparent 25%
            ),
            radial-gradient(
                circle at 95% 5%,
                rgba(196, 181, 253, 0.13),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #f5faff 0%,
                #fbf9ff 50%,
                #f5fffb 100%
            );

        color: #334e68;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 0.45rem;
        padding-bottom: 1.5rem;
    }


    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #fbfdff 0%,
                #f0f7ff 100%
            );

        border-right: 1px solid #dceaf5;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #526b84 !important;
        font-size: 0.95rem !important;
    }


    /* ---------- TOP LEFT BRAND ---------- */

    .brand {
        display: flex;
        align-items: baseline;
        gap: 7px;
        margin-top: -4px;
        margin-bottom: 0.5px;
    }

    .brand-citypulse {
        font-family: Arial, sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: 1.3px;
        color: #334e68;
    }

    .brand-delhi {
        font-family:
            "Brush Script MT",
            "Segoe Script",
            cursive;

        font-size: 1.65rem;
        font-weight: 500;

        color: #6366f1;
    }

    .brand-subtitle {
        color: #8a9caf;
        font-size: 0.72rem;
        margin-bottom: 9px;
    }

    .delhi1{
     color:black;}
    /* ---------- SECTION TITLE ---------- */

    .section-title {
        color: #405a73;
        font-size: 0.88rem;
        font-weight: 800;
        margin-top: 11px;
        margin-bottom: 6px;
    }


    /* ---------- STATUS ---------- */

    .status-card {
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
        background: white;
        box-shadow:
            0 5px 16px rgba(60, 90, 120, 0.07);
    }

    .status-good {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
    }

    .status-warning {
        background: #fffbeb;
        border: 1px solid #fde68a;
    }

    .status-danger {
        background: #fef2f2;
        border: 1px solid #fecaca;
    }

    .status-label {
        color: #64748b;
        font-size: 0.70rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .status-main {
        font-size: 1rem;
        font-weight: 850;
        margin-top: 2px;
    }

    .status-sub {
        color: #718096;
        font-size: 0.74rem;
        margin-top: 2px;
    }


    /* ---------- DATA CARDS ---------- */

    .data-card {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid #deebf5;
        border-radius: 14px;
        padding: 11px;
        min-height: 88px;

        box-shadow:
            0 5px 15px rgba(60, 90, 120, 0.06);
    }

    .data-icon {
        font-size: 1rem;
    }

    .data-label {
        color: #718096;
        font-size: 0.74rem;
        font-weight: 700;
        margin-top: 2px;
    }

    .data-value {
        color: #334e68;
        font-size: 0.95rem;
        font-weight: 850;
        margin-top: 2px;
    }

    .data-note {
        color: #94a3b8;
        font-size: 0.72rem;
        margin-top: 1px;
    }


    /* ---------- CONDITION ---------- */

    .condition-card {
        background:
            linear-gradient(
                135deg,
                #eef8ff,
                #f7f2ff
            );

        border: 1px solid #dce8f4;
        border-radius: 17px;
        padding: 16px;

        box-shadow:
            0 6px 18px rgba(70, 100, 130, 0.07);
    }

    .condition-label {
        color: #718096;
        font-size: 0.76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .condition-score {
        font-size: 2.4rem;
        line-height: 1;
        font-weight: 900;
        margin-top: 5px;
    }

    .green {
        color: #16a34a;
    }

    .orange {
        color: #d97706;
    }

    .red {
        color: #dc2626;
    }

    .condition-status {
        color: #334e68;
        font-size: 0.95rem;
        font-weight: 850;
        margin-top: 4px;
    }

    .condition-description {
        color: #718096;
        font-size: 0.68rem;
        margin-top: 4px;
        line-height: 1.4;
    }


    /* ---------- INSIGHT ---------- */

    .insight-card {
        background: rgba(255,255,255,0.94);
        border: 1px solid #e0eaf3;
        border-radius: 17px;
        padding: 16px;

        box-shadow:
            0 6px 18px rgba(60, 90, 120, 0.06);
    }

    .insight-title {
        color: #405a73;
        font-size: 0.88rem;
        font-weight: 850;
        margin-bottom: 6px;
    }

    .insight-text {
        color: #687d92;
        font-size: 0.72rem;
        line-height: 1.5;
    }


    /* ---------- PILLS ---------- */

    .pill {
        display: inline-block;

        padding: 4px 7px;
        margin-right: 3px;
        margin-top: 5px;

        border-radius: 999px;

        background: #f8fafc;
        border: 1px solid #e2e8f0;

        color: #64748b;
        font-size: 0.65rem;
        font-weight: 700;
    }


    /* ---------- BUTTON ---------- */

    .stButton > button {
        border-radius: 10px;
        border: none;

        background:
            linear-gradient(
                90deg,
                #60a5fa,
                #818cf8
            );

        color: white;
        font-size: 0.76rem;
        font-weight: 750;

        box-shadow:
            0 4px 12px rgba(99, 102, 241, 0.15);
    }

    .stButton > button:hover {
        background:
            linear-gradient(
                90deg,
                #3b82f6,
                #6366f1
            );

        color: white;
    }


    /* ---------- METRICS ---------- */

    [data-testid="stMetricLabel"] {
        font-size: 0.69rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.05rem !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.72rem !important;
    }


    /* ---------- EXPANDERS ---------- */

    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.88);
        border: 1px solid #deebf5;
        border-radius: 12px;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #9aaabd;
        font-size: 0.60rem;
        padding-top: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.html(
    """

    <div class="brand" style="display: flex; flex-direction: column;">
        <div class="brand-citypulse">CITYPULSE</div>
        <div class="brand-delhi">Delhi</div>
    </div>
    
    <div class="brand-subtitle">
        Live civic conditions at a glance
    </div>
    """
)


    st.html("""<div class="delhi1">🧭 Explore Delhi</div>""")

    zone = st.selectbox(
        "Choose an area",
        [
            "All Delhi",
            "Central Delhi",
            "South Delhi",
            "East Delhi",
            "West Delhi",
            "North West Delhi",
        ],
    )

    st.markdown("### 🗺️ Map layers")

    show_weather = st.checkbox(
        "🌧️ Weather",
        value=True,
    )

    show_air = st.checkbox(
        "🌫️ Air quality",
        value=True,
    )

    show_incidents = st.checkbox(
        "🚨 Local problems",
        value=True,
    )

    show_transit = st.checkbox(
        "🚍 Public transport",
        value=True,
    )

    st.write("")

    refresh = st.button(
        "🔄 Refresh data",
        width="stretch",
        key="refresh_data",
    )

    st.divider()

    st.caption("About this demo")

    st.caption(
        "Local problem reports are synthetic "
        "for the hackathon demonstration. "
        "They are not official government complaints."
    )


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(ttl=300)
def get_data():

    weather = load_weather()
    air = load_air()
    transit = load_transit()
    incidents = make_incidents()

    return (
        weather,
        air,
        transit,
        incidents,
    )


if refresh:

    st.cache_data.clear()
    st.rerun()


weather, air, transit, incidents = get_data()


# =========================================================
# AREA MAP CENTERS
# =========================================================

area_centers = {

    "All Delhi":
        ([28.6139, 77.2090], 10),

    "Central Delhi":
        ([28.6328, 77.2197], 12),

    "South Delhi":
        ([28.5433, 77.2066], 12),

    "East Delhi":
        ([28.6469, 77.3161], 12),

    "West Delhi":
        ([28.6517, 77.1171], 12),

    "North West Delhi":
        ([28.7041, 77.1025], 12),
}
# =========================
# TRAFFIC STATUS
# =========================

traffic_data = {
    "All Delhi": {
        "status": "Moderate",
        "level": 58,
        "color": "darkorange",
        "description": "Traffic is moving with some delays across major roads."
    },
    "Central Delhi": {
        "status": "Heavy",
        "level": 82,
        "color": "red",
        "description": "Busy roads and slower movement are expected around central areas."
    },
    "South Delhi": {
        "status": "Moderate",
        "level": 55,
        "color": "darkorange",
        "description": "Traffic is generally moving, with some congestion on major routes."
    },
    "East Delhi": {
        "status": "Heavy",
        "level": 78,
        "color": "red",
        "description": "Higher congestion is estimated around major connecting roads."
    },
    "West Delhi": {
        "status": "Moderate",
        "level": 60,
        "color": "darkorange",
        "description": "Traffic is moderately busy with occasional slowdowns."
    },
    "North West Delhi": {
        "status": "Light",
        "level": 32,
        "color": "green",
        "description": "Traffic is relatively light and roads are moving smoothly."
    },
}

traffic = traffic_data.get(
    zone,
    traffic_data["All Delhi"]
)

# Traffic section
st.markdown("### 🚦 Traffic in this area")



if traffic["color"] == "green":
    st.success(
        f'🟢 {traffic["description"]}'
    )

elif traffic["color"] == "darkorange":
    st.markdown("""
<div style="
    background-color: #FFF4CC;
    #border-left: 5px  #E6B800;
    padding: 12px 16px;
    border-radius: 8px;
    color: #5C4A00;
    font-size: 18px;
    font-color: darkyellow;
">
    🟡 Traffic is moderate
</div>
""", unsafe_allow_html=True)

else:
    st.error(
        f'🔴 {traffic["description"]}'
    )

st.caption(
    "ℹ️ Traffic values are demonstration estimates for the hackathon MVP, "
    "not live traffic data."
)

# =========================================================
# AREA INCIDENTS
# =========================================================

if zone == "All Delhi":

    area_incidents = incidents.copy()

else:

    area_incidents = incidents[
        incidents["zone"] == zone
    ].copy()


# =========================================================
# AREA AIR QUALITY
# =========================================================

base_pm25 = float(
    air["pm25"]
)


# Demo adjustments to create
# visible area-level variation.
#
# These are NOT official
# neighbourhood measurements.

area_air_adjustments = {

    "All Delhi": 0,

    "Central Delhi": 10,

    "South Delhi": -10,

    "East Delhi": 18,

    "West Delhi": 5,

    "North West Delhi": 14,
}


local_pm25 = max(
    5,
    base_pm25
    +
    area_air_adjustments.get(
        zone,
        0,
    ),
)


area_air = air.copy()

area_air["pm25"] = local_pm25


# =========================================================
# CITYPULSE SCORE
# =========================================================

score = pulse_score(
    weather,
    area_air,
    area_incidents,
)


# =========================================================
# AIR QUALITY STATUS
# =========================================================

if local_pm25 <= 60:

    air_status = "Good"

elif local_pm25 <= 100:

    air_status = "Elevated"

else:

    air_status = "Poor"


# =========================================================
# CITY STATUS
# =========================================================

if score >= 75:

    area_status = "Looking good"

    status_class = "status-good"

    score_class = "green"

    status_icon = "🟢"

elif score >= 50:

    area_status = "Needs improvement"

    status_class = "status-warning"

    score_class = "orange"

    status_icon = "🟠"

else:

    area_status = "Difficult conditions"

    status_class = "status-danger"

    score_class = "red"

    status_icon = "🔴"


# =========================================================
# RECENT INCIDENTS
# =========================================================

if len(area_incidents) > 0:

    latest_time = (
        area_incidents["timestamp"].max()
    )

    recent_count = len(
        area_incidents[
            area_incidents["timestamp"]
            >=
            latest_time
            -
            pd.Timedelta(hours=2)
        ]
    )

else:

    recent_count = 0


# =========================================================
# WEATHER HELPER
# =========================================================

def get_weather_value(
    key,
    default_value,
):

    try:

        value = weather.get(
            key,
            None,
        )

        if value is None:

            return default_value

        return float(value)

    except (
        TypeError,
        ValueError,
        AttributeError,
    ):

        return default_value


temperature = get_weather_value(
    "temperature",
    30,
)

humidity = get_weather_value(
    "humidity",
    68,
)

wind_speed = get_weather_value(
    "wind_speed",
    14,
)

feels_like = get_weather_value(
    "feels_like",
    temperature + 3,
)

uv_index = get_weather_value(
    "uv_index",
    7,
)


# =========================================================
# UV STATUS
# =========================================================

if uv_index <= 2:

    uv_status = "Low"

elif uv_index <= 5:

    uv_status = "Moderate"

elif uv_index <= 7:

    uv_status = "High"

elif uv_index <= 10:

    uv_status = "Very high"

else:

    uv_status = "Extreme"


# =========================================================
# TOP STATUS
# =========================================================

st.html(
        f"""
        <div class="condition-card">

            <div class="condition-label">
                {zone} condition
            </div>

            <div class="condition-score {score_class}">
                {score}
            </div>

            <div class="condition-status">
                {area_status}
            </div>

            <div class="condition-description">
                Based on air quality,
                weather and local reports.
            </div>

        </div>
        """
    )


# =========================================================
# ENVIRONMENT
# =========================================================

st.markdown(
    '<div class="section-title">☀️ Today\'s environment</div>',
    unsafe_allow_html=True,
)


env1, env2, env3, env4, env5 = st.columns(5)


with env1:

    st.html(
        f"""
        <div class="data-card">

            <div class="data-icon">
                ☀️
            </div>

            <div class="data-label">
                UV index
            </div>

            <div class="data-value">
                {uv_index:.0f}
            </div>

            <div class="data-note">
                {uv_status}
            </div>

        </div>
        """
    )


with env2:

    st.html(
        f"""
        <div class="data-card">

            <div class="data-icon">
                🌫️
            </div>

            <div class="data-label">
                Air quality
            </div>

            <div class="data-value">
                {air_status}
            </div>

            <div class="data-note">
                PM2.5: {local_pm25:.0f}
            </div>

        </div>
        """
    )


with env3:

    st.html(
        f"""
        <div class="data-card">

            <div class="data-icon">
                🌡️
            </div>

            <div class="data-label">
                Temperature
            </div>

            <div class="data-value">
                {temperature:.0f}°C
            </div>

            <div class="data-note">
                Feels like {feels_like:.0f}°C
            </div>

        </div>
        """
    )


with env4:

    st.html(
        f"""
        <div class="data-card">

            <div class="data-icon">
                💧
            </div>

            <div class="data-label">
                Humidity
            </div>

            <div class="data-value">
                {humidity:.0f}%
            </div>

            <div class="data-note">
                Current estimate
            </div>

        </div>
        """
    )


with env5:

    st.html(
        f"""
        <div class="data-card">

            <div class="data-icon">
                🌬️
            </div>

            <div class="data-label">
                Wind
            </div>

            <div class="data-value">
                {wind_speed:.0f} km/h
            </div>

            <div class="data-note">
                Current estimate
            </div>

        </div>
        """
    )


# =========================================================
# MAP
# =========================================================

st.markdown(
    '<div class="section-title">🗺️ What\'s happening around Delhi?</div>',
    unsafe_allow_html=True,
)


map_center, map_zoom = area_centers[
    zone
]


m = folium.Map(
    location=map_center,
    zoom_start=map_zoom,
    tiles="OpenStreetMap",
)


# =========================================================
# INCIDENT MARKERS
# =========================================================

if show_incidents:

    for _, row in area_incidents.tail(100).iterrows():

        category = row["category"]


        if category in [
            "Traffic",
            "Waterlogging",
        ]:

            marker_color = "red"

        else:

            marker_color = "orange"


        folium.CircleMarker(

            location=[
                row["lat"],
                row["lon"],
            ],

            radius=6,

            color=marker_color,

            fill=True,

            fill_opacity=0.75,

            popup=(
                f"{category} · "
                f"{row['place']} · "
                f"{row['zone']}"
            ),

        ).add_to(m)


# =========================================================
# WEATHER MARKER
# =========================================================

if show_weather:

    folium.Marker(

        map_center,

        tooltip=(
            f"{zone} weather · "
            f"{temperature:.1f}°C"
        ),

    ).add_to(m)


# =========================================================
# AIR QUALITY MARKERS
# =========================================================

if show_air:

    air_stations = [

        (
            "ITO",
            28.6289,
            77.2506,
            "Central Delhi",
        ),

        (
            "R K Puram",
            28.5633,
            77.1869,
            "South Delhi",
        ),

        (
            "Anand Vihar",
            28.6469,
            77.3161,
            "East Delhi",
        ),

    ]


    for (
        place,
        lat,
        lon,
        station_zone,
    ) in air_stations:


        should_show = (

            zone == "All Delhi"

            or

            station_zone == zone

        )


        if should_show:

            folium.CircleMarker(

                [lat, lon],

                radius=7,

                color="purple",

                fill=True,

                fill_opacity=0.75,

                popup=(
                    f"Air station: {place} · "
                    f"{station_zone} · "
                    f"PM2.5: {local_pm25:.0f}"
                ),

            ).add_to(m)


# =========================================================
# TRANSIT
# =========================================================

if show_transit:

    transit_hubs = [

        (
            "Rajiv Chowk",
            28.6328,
            77.2197,
        ),

        (
            "Hauz Khas",
            28.5433,
            77.2066,
        ),

        (
            "Kashmere Gate",
            28.6675,
            77.2282,
        ),

        (
            "Dwarka",
            28.5921,
            77.0460,
        ),

    ]


    for name, lat, lon in transit_hubs:

        folium.Marker(

            [lat, lon],

            tooltip=(
                f"Transit hub: {name}"
            ),

            icon=folium.Icon(
                color="blue",
                icon="train",
                prefix="fa",
            ),

        ).add_to(m)


# =========================================================
# DISPLAY MAP
# =========================================================

st_folium(
    m,
    width=None,
    height=450,
)


# =========================================================
# CITY CONDITION
# =========================================================

st.markdown(
    '<div class="section-title">💓 City condition</div>',
    unsafe_allow_html=True,
)



    



st.html(
        f"""
        <div class="insight-card">

            <div class="insight-title">
                💡 {zone}
            </div>

            <div class="insight-text">

                Air quality is
                <b>{air_status.lower()}</b>,
                with PM2.5 around
                <b>{local_pm25:.0f}</b>.

                There are
                <b>{recent_count}</b>
                local problem reports
                in the recent two-hour window.

            </div>

            <div>

                <span class="pill">
                    🌫️ Air: {air_status}
                </span>

                <span class="pill">
                    ☀️ UV: {uv_status}
                </span>

                <span class="pill">
                    🚨 Reports: {recent_count}
                </span>

                <span class="pill">
                    🚍 Transit: Available
                </span>

            </div>

        </div>
        """
    )



# =========================================================
# PLAN YOUR JOURNEY
# =========================================================

st.html(
    """
    <div class="section-title">
        🧭 Plan your journey
    </div>

    <div class="insight-card">

        <div class="insight-title">
            📍 Where are you going?
        </div>

        <div class="insight-text">
            Choose your starting point and destination
            to get a quick travel estimate.
        </div>

    </div>
    """
)


# =========================================================
# DELHI LOCATIONS
# =========================================================

delhi_locations = {
    # Central Delhi
    "Connaught Place": (28.6315, 77.2167),
    "India Gate": (28.6129, 77.2295),
    "Jantar Mantar": (28.6271, 77.2166),
    "Rashtrapati Bhavan": (28.6143, 77.1994),
    "Rajiv Chowk": (28.6328, 77.2197),
    "Khan Market": (28.6001, 77.2273),

    # Old Delhi
    "Red Fort": (28.6562, 77.2410),
    "Chandni Chowk": (28.6506, 77.2303),
    "Jama Masjid": (28.6507, 77.2334),
    "Kashmere Gate": (28.6675, 77.2282),

    # South Delhi
    "Qutub Minar": (28.5244, 77.1855),
    "Hauz Khas": (28.5494, 77.2001),
    "Lodhi Garden": (28.5933, 77.2197),
    "Lotus Temple": (28.5535, 77.2588),
    "Nehru Place": (28.5491, 77.2510),
    "Saket": (28.5244, 77.2066),
    "Greater Kailash": (28.5419, 77.2380),

    # East Delhi
    "Akshardham": (28.6127, 77.2773),
    "Anand Vihar": (28.6469, 77.3161),
    "Mayur Vihar": (28.6047, 77.2948),
    "Laxmi Nagar": (28.6304, 77.2773),

    # West Delhi
    "Rajouri Garden": (28.6424, 77.1227),
    "Janakpuri": (28.6219, 77.0878),
    "Dwarka": (28.5921, 77.0460),
    "Tilak Nagar": (28.6363, 77.0965),

    # North Delhi
    "North Campus": (28.6892, 77.2115),
    "Civil Lines": (28.6761, 77.2250),
    "Model Town": (28.7158, 77.1910),

    # North West Delhi
    "Rohini": (28.7495, 77.0565),
    "Pitampura": (28.7033, 77.1322),
    "Shalimar Bagh": (28.7170, 77.1500),

    # Airport
    "Delhi Airport": (28.5562, 77.1000),

    # NCR
    "Noida Sector 18": (28.5708, 77.3260),
    "Noida City Centre": (28.5746, 77.3560),
    "Gurugram Cyber Hub": (28.4946, 77.0895),
    "Gurugram MG Road": (28.4794, 77.0920),
    "Ghaziabad": (28.6692, 77.4538),
    "Faridabad": (28.4089, 77.3178),
}
# =========================================================
# LOCATION SELECTORS
# =========================================================

location_names = list(
    delhi_locations.keys()
)


from_col, to_col = st.columns(2)


with from_col:

    from_place = st.selectbox(
        "📍 From",
        location_names,
        index=0,
        key="journey_from",
    )


with to_col:

    to_place = st.selectbox(
        "📍 To",
        location_names,
        index=1,
        key="journey_to",
    )

# =========================================================
# JOURNEY CALCULATION
# =========================================================

if from_place == to_place:

    st.warning(
        "Please choose two different locations."
    )

else:

    from_lat, from_lon = (
        delhi_locations[from_place]
    )

    to_lat, to_lon = (
        delhi_locations[to_place]
    )


    # =====================================================
    # DISTANCE
    # =====================================================

    import math


    def haversine_distance(
        lat1,
        lon1,
        lat2,
        lon2,
    ):

        earth_radius = 6371.0

        lat1_rad = math.radians(lat1)

        lat2_rad = math.radians(lat2)

        delta_lat = math.radians(
            lat2 - lat1
        )

        delta_lon = math.radians(
            lon2 - lon1
        )

        a = (
            math.sin(delta_lat / 2) ** 2
            +
            math.cos(lat1_rad)
            *
            math.cos(lat2_rad)
            *
            math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )

        return earth_radius * c


    distance_km = haversine_distance(
        from_lat,
        from_lon,
        to_lat,
        to_lon,
    )


    # =====================================================
    # ESTIMATED TRAVEL TIMES
    # =====================================================

    driving_minutes = max(
        5,
        round(
            (distance_km / 22) * 60
        ),
    )


    transit_minutes = max(
        8,
        round(
            (distance_km / 17) * 60 + 7
        ),
    )


    walking_minutes = max(
        5,
        round(
            (distance_km / 5) * 60
        ),
    )


    # =====================================================
    # RESULTS
    # =====================================================

    st.write("")


    journey1, journey2, journey3 = st.columns(3)


    with journey1:

        st.html(
            f"""
            <div class="data-card">

                <div class="data-icon">
                    🚗
                </div>

                <div class="data-label">
                    Driving estimate
                </div>

                <div class="data-value">
                    {driving_minutes} min
                </div>

                <div class="data-note">
                    Estimated, not live traffic
                </div>

            </div>
            """
        )


    with journey2:

        st.html(
            f"""
            <div class="data-card">

                <div class="data-icon">
                    🚇
                </div>

                <div class="data-label">
                    Transit estimate
                </div>

                <div class="data-value">
                    {transit_minutes} min
                </div>

                <div class="data-note">
                    Approximate journey time
                </div>

            </div>
            """
        )


    with journey3:

        st.html(
            f"""
            <div class="data-card">

                <div class="data-icon">
                    📏
                </div>

                <div class="data-label">
                    Distance
                </div>

                <div class="data-value">
                    {distance_km:.1f} km
                </div>

                <div class="data-note">
                    Straight-line distance
                </div>

            </div>
            """
        )


    # =====================================================
    # WALKING
    # =====================================================

    st.caption(
        f"🚶 Walking estimate: approximately "
        f"{walking_minutes} minutes"
    )


    # =====================================================
    # JOURNEY MAP
    # =====================================================

    st.html(
        """
        <div class="section-title">
            🗺️ Your journey
        </div>
        """)


    journey_map = folium.Map(

        location=[
            (from_lat + to_lat) / 2,
            (from_lon + to_lon) / 2,
        ],

        zoom_start=11,

        tiles="OpenStreetMap",
    )


    # =====================================================
    # START LOCATION
    # =====================================================

    folium.Marker(

        [from_lat, from_lon],

        tooltip=f"START: {from_place}",

        popup=f"Starting point: {from_place}",

        icon=folium.Icon(
            color="green",
            icon="play",
            prefix="fa",
        ),

    ).add_to(journey_map)


    # =====================================================
    # DESTINATION
    # =====================================================

    folium.Marker(

        [to_lat, to_lon],

        tooltip=f"DESTINATION: {to_place}",

        popup=f"Destination: {to_place}",

        icon=folium.Icon(
            color="red",
            icon="flag",
            prefix="fa",
        ),

    ).add_to(journey_map)


    # =====================================================
    # APPROXIMATE ROUTE
    # =====================================================

    folium.PolyLine(

        locations=[
            [from_lat, from_lon],
            [to_lat, to_lon],
        ],

        color="#6366f1",

        weight=5,

        opacity=0.75,

        tooltip="Approximate route",

    ).add_to(journey_map)


    # =====================================================
    # SHOW MAP
    # =====================================================

    st_folium(

        journey_map,

        width=None,

        height=400,

        key="journey_map",
    )


    # =====================================================
    # DISCLAIMER
    # =====================================================

    st.caption(
        "ℹ️ Travel times are demonstration estimates. "
        "The route shown is a straight-line approximation "
        "and is not a turn-by-turn navigation route."
    )
# =========================================================
# TECHNICAL DETAILS
# =========================================================

with st.expander("🔬 Technical details"):

    st.markdown(
        """
        **CityPulse pipeline**

        Weather + air quality + transit +
        local civic events are combined into
        a resident-friendly city condition view.

        The selected area filters the synthetic
        local-event data and changes the map view.

        The CityPulse score is a simplified
        0–100 demonstration score.

        Area-level air-quality variation in this
        MVP is a demonstration adjustment and
        should not be interpreted as an official
        neighbourhood measurement.
        """
    )


# =========================================================
# DATA LIMITATIONS
# =========================================================

with st.expander("📚 Data sources & limitations"):

    st.markdown(
        """
        - Weather: project weather source / fallback.
        - Air quality: project air-quality source.
        - Transit: Delhi static transit data.
        - Local problems: synthetic hackathon data.
        - Map: OpenStreetMap through Folium.
        - UV, humidity and wind may use demo estimates
          when the source does not provide those fields.
        -Traffic information :synthetic data for demo
        Synthetic local reports are not official
        government complaints.
        """
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        CityPulse Delhi · Hackathon MVP
    </div>
    """,
    unsafe_allow_html=True,
)