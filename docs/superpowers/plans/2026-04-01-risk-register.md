# Lime Risk Register Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only Flask dashboard for Lime's global risk manager showing all markets grouped by country with risk levels, auto-generated GR note tags, and filters.

**Architecture:** Single Flask app with a `load_data()` abstraction that reads `Markets.csv` and runs a keyword-based auto-tagger. One Jinja2 template renders the full page; client-side JS handles filter show/hide. No database.

**Tech Stack:** Python 3, Flask, pandas, Jinja2, plain CSS, gunicorn (Railway deployment)

---

## File Map

| File | Responsibility |
|---|---|
| `app.py` | Flask app, Basic Auth, `/` route, `load_data()`, `tag_notes()` |
| `data/Markets.csv` | Source data (copied from Downloads) |
| `templates/index.html` | Full page: header, stats, filters, country-grouped table |
| `static/style.css` | All styles: layout, badges, tag pills, table |
| `requirements.txt` | Flask, pandas, gunicorn |
| `Procfile` | `web: gunicorn app:app` |
| `tests/test_app.py` | Tests for `tag_notes()` and `load_data()` |

---

## Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `Procfile`
- Create: `.gitignore`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
Flask==3.0.3
pandas==2.2.2
gunicorn==21.2.0
```

- [ ] **Step 2: Create Procfile**

```
web: gunicorn app:app
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.env
venv/
*.db
.DS_Store
```

- [ ] **Step 4: Create tests/__init__.py**

Empty file:
```python
```

- [ ] **Step 5: Create data/ directory and copy CSV**

```bash
mkdir -p /Users/arthursmith/lime-risk-register/data
cp "/Users/arthursmith/Downloads/🌆Markets.csv" /Users/arthursmith/lime-risk-register/data/Markets.csv
```

- [ ] **Step 6: Commit**

```bash
cd /Users/arthursmith/lime-risk-register
git add requirements.txt Procfile .gitignore tests/ data/
git commit -m "feat: project scaffold and data file"
```

---

## Task 2: Auto-Tagger (TDD)

**Files:**
- Create: `app.py` (tagger only for now)
- Create: `tests/test_app.py`

- [ ] **Step 1: Write failing tests for tag_notes()**

Create `tests/test_app.py`:

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import tag_notes

def test_rfp_tag():
    tags = tag_notes("RFP response submitted January 2026")
    assert "RFP / Tender" in tags

def test_escalation_tag():
    tags = tag_notes("GR dealing with significant escalation")
    assert "Active Escalation" in tags

def test_compliance_tag():
    tags = tag_notes("Increasing fines and impoundments issue persists.")
    assert "Compliance" in tags

def test_competition_tag():
    tags = tag_notes("Potential to benefit from decline in Dott scooter performance")
    assert "Competition" in tags

def test_data_sharing_tag():
    tags = tag_notes("Escalation ongoing due to data sharing as part of new contract")
    assert "Data Sharing" in tags

def test_contract_tag():
    tags = tag_notes("Contract Extension secured Feb 2026")
    assert "Contract / MOU" in tags

def test_political_risk_tag():
    tags = tag_notes("Cabinet Lead and Council opposed to any operations")
    assert "Political Risk" in tags

def test_fleet_tag():
    tags = tag_notes("uphill battle to get fleet increases")
    assert "Fleet / Deployment" in tags

def test_relationship_tag():
    tags = tag_notes("Difficult to build a 1-1 relationship with the city")
    assert "Relationship" in tags

def test_permit_tag():
    tags = tag_notes("Ongoing campaign to retain the permit, which is at risk")
    assert "Permit / License Risk" in tags

def test_multiple_tags():
    tags = tag_notes("Contract Extension secured. RFP/Tender likely in H2 2026")
    assert "Contract / MOU" in tags
    assert "RFP / Tender" in tags

def test_empty_notes():
    tags = tag_notes("")
    assert tags == []

def test_none_notes():
    tags = tag_notes(None)
    assert tags == []
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /Users/arthursmith/lime-risk-register
python -m pytest tests/test_app.py -v
```
Expected: `ImportError` or `ModuleNotFoundError` — `app.py` doesn't exist yet.

- [ ] **Step 3: Create app.py with tag_notes() only**

```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
python -m pytest tests/test_app.py -v
```
Expected: All 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: auto-tagger with tests"
```

---

## Task 3: Data Loader

**Files:**
- Modify: `app.py` — add `load_data()`
- Modify: `tests/test_app.py` — add loader tests

- [ ] **Step 1: Add load_data() tests**

Append to `tests/test_app.py`:

```python
from app import load_data

def test_load_data_returns_list():
    markets = load_data()
    assert isinstance(markets, list)
    assert len(markets) > 0

def test_load_data_fields():
    markets = load_data()
    m = markets[0]
    assert "market" in m
    assert "status" in m
    assert "sentiment" in m
    assert "notes" in m
    assert "gr_lead" in m
    assert "regional_head" in m
    assert "country" in m
    assert "tags" in m

def test_load_data_tags_are_lists():
    markets = load_data()
    for m in markets:
        assert isinstance(m["tags"], list)

def test_load_data_red_markets_exist():
    markets = load_data()
    red = [m for m in markets if m["sentiment"] == "Red"]
    assert len(red) > 0
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
python -m pytest tests/test_app.py::test_load_data_returns_list -v
```
Expected: FAIL — `load_data` not defined.

- [ ] **Step 3: Add load_data() to app.py**

Add after the `tag_notes` function:

```python
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
```

Also add `import os` at the top of `app.py` (first line after the existing imports):

```python
import os
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/test_app.py -v
```
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_app.py
git commit -m "feat: data loader with column mapping and tagging"
```

---

## Task 4: Flask Route + Auth

**Files:**
- Modify: `app.py` — add Basic Auth, `/` route

- [ ] **Step 1: Add Basic Auth decorator and route to app.py**

Add after `load_data()`:

```python
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
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5006))
    app.run(host="0.0.0.0", port=port, debug=True)
```

- [ ] **Step 2: Run the app and verify it starts**

```bash
cd /Users/arthursmith/lime-risk-register
python app.py
```
Expected: `Running on http://0.0.0.0:5006` — no errors.

Stop with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: flask route with basic auth"
```

---

## Task 5: HTML Template

**Files:**
- Create: `templates/index.html`

- [ ] **Step 1: Create templates/index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lime Global Risk Register</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>

<header>
  <div class="header-inner">
    <div class="logo">🟢 Lime</div>
    <div class="header-title">
      <h1>Global Risk Register</h1>
      <span class="header-date">{{ now }}</span>
    </div>
  </div>
</header>

<div class="stats-bar">
  <div class="stat">
    <span class="stat-number">{{ total }}</span>
    <span class="stat-label">Markets</span>
  </div>
  <div class="stat">
    <span class="stat-number red-num">{{ red_count }}</span>
    <span class="stat-label">🔴 Red</span>
  </div>
  <div class="stat">
    <span class="stat-number yellow-num">{{ yellow_count }}</span>
    <span class="stat-label">🟡 Yellow</span>
  </div>
</div>

<div class="filters">
  <label>Risk Level:
    <select id="filter-risk" onchange="applyFilters()">
      <option value="all">All</option>
      <option value="Red">Red</option>
      <option value="Yellow">Yellow</option>
    </select>
  </label>
  <label>Country:
    <select id="filter-country" onchange="applyFilters()">
      <option value="all">All Countries</option>
      {% for c in countries %}
      <option value="{{ c }}">{{ c }}</option>
      {% endfor %}
    </select>
  </label>
</div>

<main>
  {% for country in sorted_countries %}
  <div class="country-section" data-country="{{ country }}">
    <h2 class="country-heading">{{ country }}</h2>
    <table class="market-table">
      <thead>
        <tr>
          <th>Market</th>
          <th>Risk</th>
          <th>Tags</th>
          <th>GR Notes</th>
          <th>GR Lead</th>
          <th>Regional GR Head</th>
        </tr>
      </thead>
      <tbody>
        {% for m in by_country[country] %}
        <tr class="market-row" data-sentiment="{{ m.sentiment }}" data-country="{{ m.country }}">
          <td class="market-name">{{ m.market }}</td>
          <td>
            <span class="badge badge-{{ m.sentiment | lower }}">{{ m.sentiment }}</span>
          </td>
          <td class="tags-cell">
            {% for tag in m.tags %}
            <span class="tag tag-{{ loop.index0 % 8 }}">{{ tag }}</span>
            {% endfor %}
          </td>
          <td class="notes-cell">
            {% if m.notes %}
            <span class="notes-preview">{{ m.notes[:100] }}{% if m.notes|length > 100 %}…{% endif %}</span>
            {% if m.notes|length > 100 %}
            <span class="notes-full" style="display:none">{{ m.notes }}</span>
            <button class="expand-btn" onclick="toggleNote(this)">Show more</button>
            {% endif %}
            {% else %}
            <span class="no-notes">—</span>
            {% endif %}
          </td>
          <td class="person">{{ m.gr_lead }}</td>
          <td class="person">{{ m.regional_head }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% endfor %}
</main>

<footer>
  Data source: CSV · Snowflake integration pending
</footer>

<script>
function applyFilters() {
  const risk = document.getElementById('filter-risk').value;
  const country = document.getElementById('filter-country').value;

  document.querySelectorAll('.country-section').forEach(section => {
    const sectionCountry = section.dataset.country;
    let sectionVisible = false;

    section.querySelectorAll('.market-row').forEach(row => {
      const rowRisk = row.dataset.sentiment;
      const rowCountry = row.dataset.country;
      const riskMatch = risk === 'all' || rowRisk === risk;
      const countryMatch = country === 'all' || rowCountry === country;
      const show = riskMatch && countryMatch;
      row.style.display = show ? '' : 'none';
      if (show) sectionVisible = true;
    });

    section.style.display = sectionVisible ? '' : 'none';
  });
}

function toggleNote(btn) {
  const cell = btn.parentElement;
  const preview = cell.querySelector('.notes-preview');
  const full = cell.querySelector('.notes-full');
  if (full.style.display === 'none') {
    preview.style.display = 'none';
    full.style.display = 'inline';
    btn.textContent = 'Show less';
  } else {
    preview.style.display = 'inline';
    full.style.display = 'none';
    btn.textContent = 'Show more';
  }
}
</script>

</body>
</html>
```

- [ ] **Step 2: Add `now` to the route context in app.py**

In `app.py`, add at top:

```python
from datetime import date
```

In the `index()` function, update the `render_template` call to add `now`:

```python
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
```

- [ ] **Step 3: Verify template renders**

```bash
python app.py
```

Open `http://localhost:5006` in browser, enter `admin` / `lime2026`. Confirm page loads with markets visible.

Stop with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add templates/ app.py
git commit -m "feat: html template with filters and note expand"
```

---

## Task 6: CSS Styling

**Files:**
- Create: `static/style.css`

- [ ] **Step 1: Create static/style.css**

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #f4f5f7;
  color: #1a1a2e;
  font-size: 14px;
}

/* Header */
header {
  background: #1a1a2e;
  color: white;
  padding: 16px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 3px solid #00DE00;
}
.header-inner { display: flex; align-items: center; gap: 20px; }
.logo { font-size: 22px; font-weight: 800; color: #00DE00; letter-spacing: -0.5px; }
.header-title h1 { font-size: 18px; font-weight: 600; }
.header-date { font-size: 12px; color: #aaa; }

/* Stats bar */
.stats-bar {
  display: flex;
  gap: 32px;
  padding: 16px 32px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}
.stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.stat-number { font-size: 28px; font-weight: 700; line-height: 1; }
.stat-label { font-size: 11px; text-transform: uppercase; color: #888; letter-spacing: 0.5px; }
.red-num { color: #E53E3E; }
.yellow-num { color: #D97706; }

/* Filters */
.filters {
  display: flex;
  gap: 16px;
  padding: 12px 32px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}
.filters label { font-size: 13px; color: #555; display: flex; align-items: center; gap: 8px; }
.filters select {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 13px;
  background: white;
}

/* Main content */
main { padding: 24px 32px; max-width: 1400px; margin: 0 auto; }

.country-section { margin-bottom: 32px; }

.country-heading {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #555;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 2px solid #e2e8f0;
}

/* Table */
.market-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.market-table thead tr {
  background: #f8f9fa;
  border-bottom: 1px solid #e2e8f0;
}
.market-table th {
  padding: 10px 14px;
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #888;
}
.market-table td {
  padding: 10px 14px;
  border-bottom: 1px solid #f0f2f5;
  vertical-align: top;
}
.market-table tr:last-child td { border-bottom: none; }
.market-table tr:hover td { background: #fafbfc; }

.market-name { font-weight: 600; color: #1a1a2e; white-space: nowrap; }

/* Risk badges */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}
.badge-red { background: #FEE2E2; color: #B91C1C; }
.badge-yellow { background: #FEF3C7; color: #92400E; }

/* Tags */
.tags-cell { display: flex; flex-wrap: wrap; gap: 4px; max-width: 280px; }
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}
.tag-0 { background: #E0F2FE; color: #0369A1; }
.tag-1 { background: #F0FDF4; color: #15803D; }
.tag-2 { background: #FDF4FF; color: #7E22CE; }
.tag-3 { background: #FFF7ED; color: #C2410C; }
.tag-4 { background: #F0F9FF; color: #0C4A6E; }
.tag-5 { background: #FDF2F8; color: #9D174D; }
.tag-6 { background: #ECFDF5; color: #065F46; }
.tag-7 { background: #EFF6FF; color: #1D4ED8; }

/* Notes */
.notes-cell { max-width: 320px; font-size: 13px; color: #444; line-height: 1.5; }
.notes-preview { display: inline; }
.notes-full { display: none; white-space: pre-wrap; }
.no-notes { color: #bbb; }
.expand-btn {
  background: none;
  border: none;
  color: #00DE00;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  margin-left: 4px;
  padding: 0;
  text-decoration: underline;
}
.expand-btn:hover { color: #00b300; }

/* Person cells */
.person { font-size: 12px; color: #666; max-width: 180px; }

/* Footer */
footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: #aaa;
  border-top: 1px solid #e2e8f0;
  margin-top: 24px;
}
```

- [ ] **Step 2: Verify styling in browser**

```bash
python app.py
```

Open `http://localhost:5006`. Confirm:
- Dark header with Lime green accent
- Red/Yellow badges colored correctly
- Tag pills showing in muted pastels
- GR notes truncate with "Show more" button
- Country sections visible with divider headings

Stop with Ctrl+C.

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: dashboard styles"
```

---

## Task 7: GitHub Push + Railway Deploy

**Files:** None — deployment config only.

- [ ] **Step 1: Create GitHub repo and push**

```bash
cd /Users/arthursmith/lime-risk-register
gh repo create arthursmith-jpg/lime-risk-register --public --source=. --remote=origin --push
```

If `gh` isn't configured for the `arthursmith-jpg` account, run:
```bash
gh auth login
```
and select the `arthursmith-jpg` account before running the above.

- [ ] **Step 2: Verify all files pushed**

```bash
git log --oneline
```
Expected: 5 commits visible.

- [ ] **Step 3: Deploy on Railway**

1. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
2. Select `arthursmith-jpg/lime-risk-register`
3. Railway auto-detects Python/gunicorn from `Procfile`
4. No environment variables needed for prototype
5. Under Settings → Networking → Generate Domain

- [ ] **Step 4: Verify live deployment**

Visit the Railway-generated URL. Enter `admin` / `lime2026`. Confirm all markets load correctly.

- [ ] **Step 5: Final commit (update README if needed)**

```bash
git add .
git commit -m "chore: final deployment verification"
git push
```
