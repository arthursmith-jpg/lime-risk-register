import os
import pandas as pd
from flask import Flask, render_template, request, Response
from functools import wraps

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
