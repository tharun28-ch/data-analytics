# PlaceMux — Marketplace Analytics Dashboard
### Task 1 · Company Onboarding & Marketplace Data Model
**Phase 2 · Week 2 · Data Analyst Deliverable**
*Altrodav Technologies Pvt. Ltd.*

---

## What this is

A fully self-contained, browser-runnable analytics dashboard that fulfils both Task 1 deliverables:

| Deliverable | Status |
|---|---|
| Define liquidity metrics | ✅ Built, sourced, demoable |
| Extend the tracking plan for marketplace events | ✅ Built, 8 events, live counts |

No server, no install. Open `index.html` in any modern browser — everything runs in-browser using SQLite via [sql.js](https://sql.js.org/).

---

## How to run

```bash
# Option A — just open the file
open index.html          # macOS
start index.html         # Windows
xdg-open index.html      # Linux

# Option B — serve locally (avoids any CORS issues)
npx serve .
# then open http://localhost:3000
```

---

## Dashboard tabs

| Tab | What it shows |
|---|---|
| 📊 **Liquidity Metrics** | Live metric cards (Supply Depth, Demand Depth, Fill Rate, Time-to-Fill, Match Rate) + Composite Liquidity Score ring |
| 🗂 **Tracking Plan** | All 8 marketplace events: count, last-seen, freshness, decision link, daily volume chart |
| 🛡 **Sanity & Freshness** | 11 automated assertions: row counts, null checks, dupe checks, pipeline freshness |
| 🏢 **Company Onboarding** | Live form — sign up a company, watch Supply Depth update in real time |
| ⚙️ **SQL Explorer** | The exact SQL powering every metric, runnable live |
| 📖 **Metric Dictionary** | Full source-of-truth: formula, source events, thresholds, DPDP note, owner |

---

## Liquidity metrics defined

| Metric | Formula | Source Event(s) | Decision |
|---|---|---|---|
| **Composite Liquidity Score** | Weighted combination of all 5 signals, 0–100 | All events | < 40 → investigate. > 70 → scale. |
| **Supply Depth** | `active_jobs / active_companies` | `job_posted` | < 3 → company activation campaign |
| **Demand Depth** | `active_students / active_jobs` | `student_registered` | < 1.5 → college partner outreach |
| **Fill Rate** | `hired / total_applications × 100` | `application_status_changed` | < 5% → review matching algo |
| **Time-to-Fill** | `avg(filled_at − posted_at)` days | `job_posted`, `application_status_changed` | > 14d → review shortlisting SLAs |
| **Match Rate** | `passed_threshold / total × 100` | `skill_match_evaluated` | < 30% → threshold too strict |

---

## Tracking plan (8 events added)

| Event | Trigger | Decision link |
|---|---|---|
| `company_signed_up` | Company completes onboarding | Funnel entry / onboarding conversion |
| `job_posted` | Job goes live | Supply signal |
| `student_registered` | Student profile created | Demand signal |
| `application_submitted` | Student applies | Application volume & velocity |
| `skill_match_evaluated` | System scores skill match | Match rate KPI |
| `application_status_changed` | Status updated (shortlisted/rejected/hired) | Fill rate, time-to-fill |
| `search_performed` | Discovery search executed | Search latency SLA, discovery health |
| `dashboard_viewed` | Company views candidate list | Engagement, active employer signal |

---

## Database schema

```sql
companies          -- onboarded employers
jobs               -- job postings per company
students           -- candidate pool
applications       -- student ↔ job applications + match_score + status
marketplace_events -- raw event log (tracking plan landing table)
metric_snapshots   -- daily liquidity score history
```

**Seed data:** 10 companies · ~50 jobs · 200 students · 500 applications · ~1,200 events · 30-day history

---

## Sanity & freshness checks (automated)

Every dashboard load runs 11 SQL assertions:

- Row counts > 0 for all 5 tables
- All 8 event types present in event log
- Zero null `match_score` values
- Zero null `event_name` values
- Zero duplicate applications
- Data freshness < 24 hours

Failed checks surface as red ✗ FAIL badges with a prescribed remediation action.

---

## 2-minute demo script

1. **Open** `index.html` → dashboard loads with live numbers
2. **Metrics tab** → point at Liquidity Score (ring chart), explain the composite formula
3. **Click any metric card** → jumps to SQL Explorer tab showing the exact query
4. **Tracking Plan tab** → show all 8 events, counts, freshness status, daily volume bar chart
5. **Onboarding tab** → fill in a company name, click *Sign Up* → watch Supply Depth update, event feed fires
6. **Sanity tab** → show all 11 assertions passing green

---

## Files

```
Task 1/
├── index.html   ← entire app (HTML + CSS + JS + SQLite in-browser)
└── README.md    ← this file
```

---

## Scoring self-check

| Criterion | Evidence |
|---|---|
| Liquidity metrics built, working & demoable | ✅ 5 metrics + composite score, live SQL |
| Tracking plan built, working & demoable | ✅ 8 events, counts, freshness, chart |
| Real data quality & correctness | ✅ 500 apps, 1200+ events, sanity checks |
| Live verification & evidence | ✅ All queries runnable in SQL Explorer |
| Dependency & edge-case handling | ✅ Null checks, dupe checks, freshness SLA |
