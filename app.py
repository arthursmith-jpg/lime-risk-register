import os
import pandas as pd
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

def load_data():
    df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "Market": "market",
        "Market Status": "status",
        "Market Sentiment_GR": "sentiment",
        "GR Notes": "notes",
        "GR Lead": "gr_lead",
        "Regional GR Head": "regional_head",
        "Brand/ Marketing Lead": "brand_lead",
        "Comms Lead": "comms_lead",
        "Country": "country",
    })
    df["notes"] = df["notes"].fillna("")
    df["gr_lead"] = df["gr_lead"].fillna("")
    df["regional_head"] = df["regional_head"].fillna("")
    df["country"] = df["country"].fillna("Unknown")
    df["tags"] = df["notes"].apply(tag_notes)
    markets = df.to_dict(orient="records")
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

    return render_template(
        "index.html",
        by_country=by_country,
        sorted_countries=sorted_countries,
        total=total,
        red_count=red_count,
        yellow_count=yellow_count,
        countries=countries,
        now=date.today().strftime("%B %d, %Y"),
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    app.run(host="0.0.0.0", port=port, debug=True)
