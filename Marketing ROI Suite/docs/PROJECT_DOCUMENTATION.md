# Marketing ROI Suite — Project Documentation

> **Budget:** Rs. 6,00,000 | **City:** Bangalore | **Campaigns:** 25  
> **Tools:** Python · Pandas · Matplotlib · Seaborn · SciPy

---

## Table of Contents

1. [Project Overview](#1-project-overview)  
2. [Folder Structure](#2-folder-structure)  
3. [The Dataset — What Each Column Means](#3-the-dataset)  
4. [Code Walkthrough — Line by Line](#4-code-walkthrough)  
5. [The 3 Statistical Techniques](#5-the-3-statistical-techniques)  
6. [How the Dashboard Layout Works](#6-how-the-dashboard-layout-works)  
7. [Strategic Recommendations — How They're Generated](#7-strategic-recommendations)  
8. [How to Run](#8-how-to-run)  

---

## 1. Project Overview

This project analyses a Rs. 6,00,000 marketing budget spread across **25 ad campaigns** 
running in 6 major Bangalore zones. The goal is to answer three questions:

| Question | Technique Used |
|---|---|
| Which campaigns are **failing**? | Z-Score analysis |
| Which **metrics actually drive** ROI? | Pearson Correlation Heatmap |
| What does the **ROI trend look like** as we spend more? | Linear Regression Forecast |

The final output is a single executive dashboard PNG with all three visualisations 
and a data-driven recommendation box at the bottom.

---

## 2. Folder Structure

```
Marketing ROI Suite/
├── data/
│   └── bangalore_campaigns.csv  ← The raw data (25 rows, 10 columns)
├── scripts/
│   └── marketing_roi_dashboard.py   ← The main Python script
├── docs/
│   ├── bangalore_marketing_dashboard.png  ← Generated dashboard image
│   └── PROJECT_DOCUMENTATION.md     ← This file
└── jupyter/
    └── marketing_roi_report.ipynb   ← Interactive notebook version
```

**Why this structure?**  
- `data/` keeps raw data separate from code — you never accidentally overwrite it  
- `scripts/` holds executable code  
- `docs/` holds outputs and documentation  
- `jupyter/` holds the notebook for interactive exploration and presentation  

---

## 3. The Dataset

File: `data/bangalore_campaigns.csv`

| Column | Type | What It Means | Example |
|---|---|---|---|
| `Campaign_ID` | String | Unique campaign label | CMP_001 |
| `Channel` | String | Marketing platform used | Google Ads, Instagram Ads |
| `Location` | String | Bangalore zone targeted | Koramangala, Whitefield |
| `Spend` | Float | Money spent on this campaign (in Rs.) | 26403.12 |
| `Clicks` | Int | How many people clicked the ad | 3563 |
| `Conversions` | Int | How many clicks turned into a sale/signup | 84 |
| `Revenue` | Float | Total revenue generated from conversions | 288958.88 |
| `ROI_Percentage` | Float | Return on Investment = `(Revenue - Spend) / Spend × 100` | 994.41 |
| `ROI_Z_Score` | Float | How far this campaign's ROI is from the average (in standard deviations) | 2.44 |
| `Status` | String | "Failed" if Z-Score < -1.0, else "Active/Successful" | Active/Successful |

**Key points:**
- All 25 campaign spends add up to Rs. 6,00,000
- Channels include: Google Ads, Instagram Ads, Facebook Ads, LinkedIn Ads, Influencer Marketing, Outdoor (Billboards)
- Zones include: Koramangala, Indiranagar, HSR Layout, Whitefield, JP Nagar, Jayanagar

---

## 4. Code Walkthrough

Here's what each section of `scripts/marketing_roi_dashboard.py` does:

### Section 1 — Imports & Paths (Lines 1–13)

```python
from pathlib import Path
import pandas as pd
import numpy as np
# ... and other visualisation/stats libraries
```

**What's happening:** We import the libraries, then set up file paths using `Path` 
so the script can find the CSV and knows where to save the PNG. The paths are *relative 
to the script's own location* (`__file__`), so it works no matter where you run it from.

---

### Section 2 — Load Data (Lines 15–20)

```python
df = pd.read_csv(DATA_FILE)
```

**What's happening:** The CSV is loaded into a Pandas DataFrame. We check the file exists 
first to give a friendly error message instead of a cryptic traceback.

---

### Section 3 — Linear Regression Forecast (Lines 22–25)

```python
slope, intercept, r_val, _, _ = stats.linregress(df["Spend"], df["ROI_Percentage"])
fc_roi = intercept + slope * fc_spend
```

**What's happening:**  
- `linregress()` fits a straight line through (Spend, ROI%) data points  
- `slope` = how much ROI changes per Rs. 1 of additional spend  
- `intercept` = the predicted ROI if spend were 0  
- `r_val` = correlation strength (-1 to +1)  
- We then generate 200 evenly-spaced spend values and predict their ROI for the trend line

**Why this matters:** It tells us whether spending more money generally gives better or worse returns.

---

### Section 4 — Derived Statistics (Lines 27–33)

```python
failed_df    = df[df["Status"] == "Failed"]
best_channel = df.groupby("Channel")["ROI_Percentage"].mean().idxmax()
```

**What's happening:** We pre-compute the numbers that will appear in the recommendation box:
- How many campaigns failed (Z-Score below -1.0)
- How much budget is "at risk" in those failed campaigns
- Which channel has the highest average ROI (best) and lowest (worst)

---

### Section 5 — Figure Setup & Layout (Lines 35–73)

```python
outer = gridspec.GridSpec(3, 1, height_ratios=[2.2, 2.0, 0.55], ...)
```

**What's happening:**  
We create a `24×18 inch` figure divided into **3 rows**:

| Row | Height Ratio | Contents |
|---|---|---|
| Row 0 | 2.2 | Bar chart (full width) |
| Row 1 | 2.0 | Heatmap (left) + Scatter plot (right) |
| Row 2 | 0.55 | Recommendation text box |

Using `GridSpec` instead of `plt.subplots()` gives us full control over spacing — 
this is what fixed the alignment/overlap issues from the earlier version.

---

### Section 6 — Bar Chart: Campaign ROI with Z-Score Coloring (Lines 75–115)

```python
bar_colors = [FAILED_COLOR if z < -1.0 else ACTIVE_COLOR for z in df["ROI_Z_Score"]]
bars = ax1.bar(df["Campaign_ID"], df["ROI_Percentage"], color=bar_colors, ...)
```

**What's happening:**
1. Each campaign gets a bar showing its ROI%
2. Bars are coloured **blue** (active) or **red** (failed) based on Z-Score
3. Value labels are placed above positive bars and below negative ones
4. A dashed line at `y=0` separates profit from loss
5. A legend in the top-right explains the colour coding

**The Z-Score rule:** If a campaign's ROI is more than 1 standard deviation below the 
mean ROI across all campaigns, it's flagged as "Failed". This is a statistical outlier 
detection method — not arbitrary, but based on the data's own distribution.

---

### Section 7 — Correlation Heatmap (Lines 117–147)

```python
corr_matrix = df[corr_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ...)
```

**What's happening:**
1. We compute the **Pearson correlation** between 5 numeric columns
2. Seaborn draws a colour-coded matrix — red = strong positive, blue = strong negative
3. Each cell shows the exact correlation coefficient (-1.0 to +1.0)

**How to read it:**
- A value of `1.00` on the diagonal = a column correlates perfectly with itself (expected)
- High positive values between Conversions ↔ Revenue = conversions directly drive revenue
- Low or negative values between Spend ↔ ROI% = spending more doesn't guarantee better ROI

**This answers:** "What *actually* drives revenue — clicks or conversions?"

---

### Section 8 — ROI Forecast Scatter Plot (Lines 149–187)

```python
for channel, grp in df.groupby("Channel"):
    ax3.scatter(grp["Spend"], grp["ROI_Percentage"], ...)
ax3.plot(fc_spend, fc_roi, color="#e74c3c", linestyle="--", ...)
```

**What's happening:**
1. Each campaign is a dot: x = Spend, y = ROI%
2. Dot **colour** = marketing channel (each has a unique brand-aligned colour)
3. Dot **size** = number of conversions (bigger bubble = more conversions)
4. The red dashed line = the linear regression trend from Section 3
5. The legend label includes the `r` value showing correlation strength

**This answers:** "If I increase my budget, what ROI should I expect?"

---

### Section 9 — Strategic Recommendation Box (Lines 189–213)

```python
ax_rec = fig.add_subplot(outer[2])
ax_rec.axis("off")
ax_rec.text(0.5, 0.5, rec_text, ...)
```

**What's happening:**
- A dedicated axes row with all axis lines hidden (`axis("off")`)
- A styled text box with a yellow background and orange border
- The text is dynamically generated from the data — it's not hardcoded
- Uses monospace font for clean alignment of the recommendation lines

---

### Section 10 — Save (Lines 215–218)

```python
fig.savefig(OUT_FILE, dpi=200, bbox_inches="tight", facecolor=BG_COLOR)
```

Saves the entire figure as a high-resolution PNG to `docs/`.

---

## 5. The 3 Statistical Techniques

### A. Z-Score (Outlier Detection)

**Formula:** `Z = (x - μ) / σ`

- `x` = this campaign's ROI%
- `μ` = mean ROI% across all campaigns
- `σ` = standard deviation of ROI%

If Z < -1.0, the campaign's ROI is significantly below average → **Failed**.

**Why Z-Score and not just "ROI < 0"?**  
Because a campaign with -10% ROI might be fine if the average is also low. Z-Score 
measures *relative* performance against the rest of the portfolio.

### B. Pearson Correlation (Heatmap)

**Formula:** `r = Σ[(xi - x̄)(yi - ȳ)] / √[Σ(xi - x̄)² × Σ(yi - ȳ)²]`

- Measures the *linear* relationship strength between two variables
- Range: -1 (perfect inverse) to +1 (perfect positive)
- Values near 0 = no linear relationship

**In our dashboard:** Helps identify that Conversions → Revenue is the strongest 
driver, not just raw clicks.

### C. Linear Regression (Forecast)

**Formula:** `ŷ = β₀ + β₁x`

- `β₁ (slope)` = ROI change per unit spend
- `β₀ (intercept)` = predicted ROI at zero spend
- `r²` = what proportion of ROI variation is explained by spend

**In our dashboard:** The red dashed trend line in the scatter plot shows the 
predicted ROI trajectory as spend increases.

---

## 6. How the Dashboard Layout Works

```
┌──────────────────────────────────────────────────────┐
│           Rs. 6,00,000 | Bangalore Dashboard         │  ← Title
├──────────────────────────────────────────────────────┤
│                                                      │
│       Campaign ROI% Bar Chart (full width)           │  ← Row 0 (GridSpec)
│       Blue = Active | Red = Failed (Z < -1.0)        │
│                                                      │
├─────────────────────────┬────────────────────────────┤
│                         │                            │
│   Correlation Heatmap   │   ROI Forecast Scatter     │  ← Row 1 (sub-GridSpec)
│   (5×5 metric matrix)   │   (spend vs ROI, by        │
│                         │    channel colour)          │
├─────────────────────────┴────────────────────────────┤
│  ┌────────────────────────────────────────────────┐  │
│  │         STRATEGIC RECOMMENDATIONS              │  │  ← Row 2 (text axes)
│  │  1. Cut Losses  |  2. Scale Up  |  3. Audit    │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 7. Strategic Recommendations — How They're Generated

The recommendation box is **not hardcoded text**. Each line is computed from the data:

| Recommendation | Data Source |
|---|---|
| "2 campaigns failed" | `df[df["Status"] == "Failed"]` count |
| "Rs. 4,946 at risk" | Sum of `Spend` for failed campaigns |
| "Best channel is Instagram Ads" | `groupby("Channel")["ROI_Percentage"].mean().idxmax()` |
| "Worst channel is Outdoor" | `groupby("Channel")["ROI_Percentage"].mean().idxmin()` |
| "Conversions drive Revenue" | Read from the correlation heatmap values |

This means if you update the CSV with new data, the recommendations **automatically update**.

---

## 8. How to Run

```bash
# From the project root
cd "Marketing ROI Suite"

# Generate the dashboard
python3 scripts/marketing_roi_dashboard.py

# Output appears at: docs/bangalore_marketing_dashboard.png
```

For interactive exploration, open `jupyter/marketing_roi_report.ipynb` in 
VS Code or JupyterLab.



---
