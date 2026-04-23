# DAY 15 — TIME-SERIES FORECASTING

## Project Overview

| Field | Detail |
|---|---|
| Track | Data Analyst |
| Day | 15 |
| Topic | Time-Series Forecasting |
| Data Source | DAY12 / `daily_registrations.csv` |

---

## Folder Structure

```
DAY15/
├── data/
│   └── daily_registrations.csv      ← 60-day MeetMux registration history
├── scripts/
│   └── future_forecast.py           ← Sections 1–3: MA + Seasonality
└── docs/
    ├── PROJECT_DOCUMENTATION.md     ← This file
    ├── window_war.ipynb             ← Section 4: Window War experiment
    ├── trend_analysis.png           ← Output: 7-Day moving average chart
    └── window_war.png               ← Output: 3-Day vs 30-Day MA chart
```

---

## Section 1 — Components of Time-Series Data

| Component | Description | MeetMux Example |
|---|---|---|
| Trend | Long-term direction | Growing registrations month over month |
| Seasonality | Repeating cycle | More sign-ups on weekends |
| Noise | Random fluctuation | Single-day spikes from referral links |

---

## Section 2 — Moving Average (`future_forecast.py`)

**Script:** `scripts/future_forecast.py`

### What it does
- Loads `daily_registrations.csv` with `parse_dates` and `index_col='Date'` so the index is a proper `DatetimeIndex`
- Computes a **7-Day Rolling Mean** on `Registrations` — this smooths out the Monday-to-Sunday weekly cycle
- Prints a **naïve next-day forecast** using the last rolling average value
- Groups by `day_name()` to find the **peak day** of the week
- Saves the trend chart to `docs/trend_analysis.png`

### Key Output
```
Forecasted Registrations for tomorrow: <value>
Average Sign-ups by Day:
Monday       ...
Tuesday      ...
...
Peak Day: <day>
```

---

## Section 3 — Seasonality Detection

Day-of-week analysis is performed inside `future_forecast.py`:

```python
df['DayOfWeek'] = df.index.day_name()
avg_by_day = df.groupby('DayOfWeek')['Registrations'].mean().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
])
```

This pivot-style aggregation reveals which day drives the highest average registrations, allowing the marketing team to schedule campaigns around peak-traffic days.

---

## Section 4 — Window War (`window_war.ipynb`)

**Notebook:** `docs/window_war.ipynb`

| Moving Average | Window | Characteristic |
|---|---|---|
| 3-Day MA | 3 days | Highly reactive — follows noise closely |
| 30-Day MA | 30 days | Smooth — reveals true long-term trend |

### Reflection

The **3-Day MA** reacts sharply to every spike and dip — useful for detecting anomalies but unreliable for strategic planning because it amplifies short-term noise.

The **30-Day MA** smooths out weekly seasonality and random fluctuations, exposing the genuine growth trajectory of MeetMux. For a June marketing push, a strategist needs to know the stable baseline momentum of the past month — not just the last 3 days, which could be skewed by a holiday or one-off event. The 30-Day MA answers *"where is MeetMux truly heading?"* and provides a reliable foundation for budget allocation.

---

## Completion Checklist

| Task | Status |
|---|---|
| Converted string column to Pandas datetime object | ✅ |
| Calculated and visualized a rolling moving average | ✅ |
| Identified the Peak Day using group-by logic | ✅ |
| Explained trade-off between short-window and long-window MA | ✅ |

---

## Analyst Pro-Tip

Always check for **stationarity** before applying simple forecasting models. If the data has a strong upward trend (like MeetMux's growth curve), models like ARIMA or Facebook Prophet require **de-trending** the series first to produce valid predictions. The rolling MA is a great first step for visualization, but not a substitute for stationary-aware models in production.
