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
