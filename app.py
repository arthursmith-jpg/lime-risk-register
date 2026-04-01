import os
import csv
import json
from flask import Flask, render_template, request, Response
from functools import wraps
from datetime import date

app = Flask(__name__)

TAG_RULES = [
    ("Active Escalation",   ["escalation", "escalating", "formal notice", "suspend"]),
    ("RFP / Tender",        ["rfp", "tender", "bid", "proposal submitted"]),
    ("Permit / License Risk", ["permit", "license", "ban", "re-evaluated"]),
    ("Compliance",          ["compliance", "fines", "impound", "parking", "tandem", "sidewalk"]),
    ("Competition",         ["competitor", "voi", "dott", "forest", "luup", "operators"]),
    ("Data Sharing",        ["data sharing", "live data", "mds"]),
    ("Contract / MOU",      ["contract", "mou", "renegotiat"]),
    ("Political Risk",      ["council", "cabinet", "opposition", "backlash", "sentiment"]),
    ("Fleet / Deployment",  ["fleet", "ramp-up", "deployment", "cap", "vehicle availability"]),
    ("Relationship",        ["relationship", "responsive", "communication", "engagement"]),
]

def tag_notes(notes):
    if not notes:
        return []
    notes_lower = notes.lower()
    return [tag for tag, keywords in TAG_RULES if any(kw in notes_lower for kw in keywords)]

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "Markets.csv")

COORDS = {
    "Auckland": (-36.8509, 174.7645),
    "Elmshorn": (53.7547, 9.6520),
    "Cologne": (50.9333, 6.9500),
    "Dortmund": (51.5131, 7.4653),
    "Lisbon": (38.7223, -9.1393),
    "Dubai": (25.2048, 55.2708),
    "Rome": (41.9028, 12.4964),
    "Naples": (40.8518, 14.2681),
    "Washington DC (District)": (38.9072, -77.0369),
    "Stockholm (Solna)": (59.3614, 18.0010),
    "Stockholm": (59.3293, 18.0686),
    "Odense": (55.3959, 10.3883),
    "London (Islington)": (51.5416, -0.1022),
    "London (Richmond)": (51.4613, -0.3037),
    "London (Ealing)": (51.5130, -0.3089),
    "London (Tower Hamlets)": (51.5099, -0.0059),
    "London (Kensington and Chelsea)": (51.4991, -0.1938),
    "Phoenix": (33.4484, -112.0740),
    "Opfikon": (47.4333, 8.5667),
    "Heidelberg": (49.3988, 8.6724),
    "Mainz": (50.0000, 8.2711),
    "Frankfurt": (50.1109, 8.6821),
    "Darmstadt": (49.8728, 8.6512),
    "Klagenfurt": (46.6227, 14.3050),
    "Oxford": (51.7520, -1.2577),
    "Melbourne": (-37.8136, 144.9631),
    "Marseille": (43.2965, 5.3698),
    "Castlebar": (53.8564, -9.2986),
    "Bochum": (51.4818, 7.2162),
    "Gutersloh": (51.9066, 8.3784),
    "Linz": (48.3069, 14.2858),
    "Hannover": (52.3759, 9.7320),
    "Bonn": (50.7374, 7.0982),
    "London (Hackney)": (51.5450, -0.0553),
    "London (Camden)": (51.5390, -0.1426),
    "Luenen / Lünen / Lunen": (51.6139, 7.5278),
    "South Lake Tahoe": (38.9335, -119.9843),
    "Stockholm (Sundbyberg)": (59.3614, 17.9718),
    "Bari": (41.1171, 16.8719),
    "London (Barking & Dagenham)": (51.5607, 0.1247),
    "Berkeley": (37.8716, -122.2727),
    "Denver": (39.7392, -104.9903),
    "London (Hammersmith and Fulham)": (51.4927, -0.2339),
    "Little Rock": (34.7465, -92.2896),
    "London (Haringey)": (51.5906, -0.1119),
    "Manchester": (53.4808, -2.2426),
    "Mississauga ON": (43.5890, -79.6441),
    "Perth": (-31.9505, 115.8605),
    "San Francisco": (37.7749, -122.4194),
    "Verona": (45.4384, 10.9916),
    "Ruhrpott": (51.5167, 7.4333),
    "Regensburg": (49.0134, 12.1016),
    "London (Hounslow)": (51.4678, -0.3609),
    "Konstanz": (47.6633, 9.1750),
    "Nottingham": (52.9548, -1.1581),
    "London (Lewisham)": (51.4613, -0.0209),
    "Uppsala": (59.8586, 17.6389),
    "Sophia Antipolis (CASA)": (43.6167, 7.0500),
    "Queretaro": (20.5888, -100.3899),
    "Melbourne (Yarra)": (-37.8200, 144.9800),
    "London (Sutton)": (51.3618, -0.1945),
    "London (Harrow)": (51.5898, -0.3346),
    "London (Brent)": (51.5588, -0.2817),
    "Leon": (21.1221, -101.6824),
    "Lake Tahoe": (39.0968, -120.0324),
    "London (Kingston & Sutton)": (51.4085, -0.3064),
    "London (Greenwich)": (51.4934, 0.0098),
    "London (Merton)": (51.4014, -0.1956),
    "London (Barnet)": (51.6252, -0.1517),
    "London (Enfield)": (51.6538, -0.0799),
    "London (Croydon)": (51.3727, -0.1099),
    "London (Waltham Forest)": (51.5908, -0.0134),
    "London (Newham)": (51.5077, 0.0469),
    "Lake Garda": (45.6389, 10.6531),
    "London (Bromley)": (51.4057, 0.0143),
    "London (Bexley)": (51.4416, 0.1500),
    "London (Redbridge)": (51.5590, 0.0741),
    "London (Hillingdon)": (51.5441, -0.4761),
    "London (Havering)": (51.5812, 0.1837),
    "Tokyo": (35.6762, 139.6503),
}

def load_data():
    col_map = {
        "Market": "market",
        "Market Status": "status",
        "Market Sentiment_GR": "sentiment",
        "GR Notes": "notes",
        "GR Lead": "gr_lead",
        "Regional GR Head": "regional_head",
        "Brand/ Marketing Lead": "brand_lead",
        "Comms Lead": "comms_lead",
        "Country": "country",
    }
    markets = []
    with open(DATA_FILE, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            row = {k.strip(): v for k, v in row.items()}
            m = {col_map.get(k, k): (v or "") for k, v in row.items()}
            m["country"] = m.get("country") or "Unknown"
            m["tags"] = tag_notes(m.get("notes", ""))
            coords = COORDS.get(m.get("market", ""))
            m["lat"] = coords[0] if coords else None
            m["lng"] = coords[1] if coords else None
            markets.append(m)
    return markets

USERNAME = "admin"
PASSWORD = "lime2026"

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            return Response(
                "Authentication required.",
                401,
                {"WWW-Authenticate": 'Basic realm="Lime Risk Register"'}
            )
        return f(*args, **kwargs)
    return decorated

@app.route("/")
@require_auth
def index():
    markets = load_data()

    # Group by country, sort Red-first within each country
    from collections import defaultdict
    by_country = defaultdict(list)
    for m in markets:
        by_country[m["country"]].append(m)

    # Sort markets within each country: Red first, then Yellow
    sentiment_order = {"Red": 0, "Yellow": 1}
    for country in by_country:
        by_country[country].sort(key=lambda m: sentiment_order.get(m["sentiment"], 2))

    # Sort countries: those with any Red market first, then alpha
    def country_sort_key(country):
        has_red = any(m["sentiment"] == "Red" for m in by_country[country])
        return (0 if has_red else 1, country)

    sorted_countries = sorted(by_country.keys(), key=country_sort_key)

    total = len(markets)
    red_count = sum(1 for m in markets if m["sentiment"] == "Red")
    yellow_count = sum(1 for m in markets if m["sentiment"] == "Yellow")
    countries = sorted(set(m["country"] for m in markets))

    map_markets = [
        {"market": m["market"], "country": m["country"], "sentiment": m["sentiment"],
         "tags": m["tags"], "notes": m["notes"][:120] if m["notes"] else "",
         "lat": m["lat"], "lng": m["lng"]}
        for m in markets if m["lat"] is not None
    ]

    return render_template(
        "index.html",
        by_country=by_country,
        sorted_countries=sorted_countries,
        total=total,
        red_count=red_count,
        yellow_count=yellow_count,
        countries=countries,
        now=date.today().strftime("%B %d, %Y"),
        markets_json=json.dumps(map_markets),
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    app.run(host="0.0.0.0", port=port, debug=True)
