# Lime Global Risk Register — Design Spec
**Date:** 2026-04-01
**Status:** Approved

---

## Overview

A read-only internal dashboard for Lime's global risk manager to monitor market-level government relations risk across all live markets. Data sourced from `Markets.csv`; architecture designed for future Snowflake real-time integration.

---

## Stack

- **Backend:** Python 3, Flask
- **Data:** pandas CSV loader (Snowflake-ready abstraction)
- **Frontend:** Jinja2 templates, plain CSS (no JS framework)
- **Auth:** HTTP Basic Auth — `admin / lime2026`
- **Local port:** 5006
- **Deployment:** Railway via `arthursmith-jpg/lime-risk-register` GitHub repo

---

## Data Layer

A single `load_data()` function in `app.py`:
1. Reads `data/Markets.csv` into a pandas DataFrame
2. Runs keyword-based auto-tagger (see Tagging section)
3. Returns a list of market dicts

To connect Snowflake later: replace only `load_data()`. No other code changes needed.

---

## Auto-Tagging Rules

Tags are assigned via Python keyword rules at load time. Each market can have multiple tags. Rules:

| Tag | Keywords / patterns |
|---|---|
| Active Escalation | escalation, escalating, formal notice, suspend |
| RFP / Tender | rfp, tender, bid, proposal submitted |
| Permit / License Risk | permit, license, ban, re-evaluated |
| Compliance | compliance, fines, impound, parking, tandem, sidewalk |
| Competition | competitor, voi, dott, forest, luup, operators |
| Data Sharing | data sharing, live data, mds |
| Contract / MOU | contract, mou, renegotiat |
| Political Risk | council, cabinet, opposition, ban, backlash, sentiment |
| Fleet / Deployment | fleet, ramp-up, deployment, cap, vehicle availability |
| Relationship | relationship, responsive, communication, engagement |

Markets with no GR notes receive no tags.

---

## UI Layout

### 1. Header
- Lime wordmark (text-based, Lime green)
- Title: "Global Risk Register"
- Subtitle: today's date

### 2. Stats Bar
- Total markets
- 🔴 Red count (with red background pill)
- 🟡 Yellow count (with amber background pill)

### 3. Filter Bar
- Dropdown: Risk Level — All / Red / Yellow
- Dropdown: Country — All + sorted list of countries
- Filters apply client-side via lightweight inline JS (show/hide rows)

### 4. Market Table
- Grouped by **country** (country name as section header)
- Countries sorted: Red-majority countries first, then alphabetical
- Within each country: Red markets listed before Yellow
- **Columns:**
  - Market name
  - Risk badge (Red / Yellow colored pill)
  - Tags (colored pills, muted tones)
  - GR Notes — collapsed by default, click to expand full text
  - GR Lead
  - Regional GR Head

### 5. Footer
- "Data source: CSV · Snowflake integration pending"

---

## Visual Design

- Background: `#f8f9fa` (light gray)
- Header accent: `#00DE00` (Lime green)
- Red badge: `#E53E3E` background, white text
- Yellow badge: `#D97706` background, white text
- Tag pills: muted pastel backgrounds per category, small font
- Font: system sans-serif stack
- Table rows: white cards with subtle shadow, hover highlight

---

## File Structure

```
lime-risk-register/
├── app.py
├── data/
│   └── Markets.csv
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── Procfile
├── requirements.txt
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-04-01-risk-register-design.md
```

---

## Deployment

1. Push to `arthursmith-jpg/lime-risk-register`
2. Connect repo to Railway
3. Set `PORT` env var (Railway injects automatically)
4. No environment variables needed for prototype (no auth secrets — credentials hardcoded for prototype only)

---

## Out of Scope (Prototype)

- Snowflake live connection
- Edit/update functionality
- User roles or multi-user auth
- Mobile optimization
- Historical risk trend tracking
