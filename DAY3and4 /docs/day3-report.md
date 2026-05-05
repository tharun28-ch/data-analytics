# Day 3 Report — The Data Lifecycle

**Date:** 07-04-2026  
**Track:** Data Analyst  
**Name:** Tharun

---

## Setup Status

Environment fully operational:

- **Python** — installed, running via VS Code terminal (`python3 --version` confirmed)  
- **VS Code** — active with Python extension enabled  
- **Pandas & Matplotlib** — installed via pip, no import errors  
- **SQL** — practiced using SQLite (`database.db`)  
- **Git** — initialized in project folder, remote set to GitHub

---

## Task Inventory

### Section 1 — Spreadsheet Architecture (Excel)
- Created spreadsheet with columns: Name, Age, Salary, City  
- Entered 20+ rows with varied cities and salary ranges  
- Sorted salaries descending, applied filters, calculated Average Salary & Total Payroll  
- Exported as `yourfile.csv`

### Section 2 — Programmatic Analysis (Python & Pandas)
- Loaded `yourfile.csv` into Pandas  
- Ran `df.head()`, `df.info()`, `df.describe()`  
- Checked for missing values (`df.isnull().sum()`)  
- Exported cleaned dataset as `cleaned_data.csv`

### Section 3 — Visual Storytelling (Matplotlib)
- Bar chart: Average Salary by City → `bar_chart.png`  
- Histogram: Salary distribution → `histogram.png`

### Section 4 — Structured Queries (SQL)
- Created `database.db` and `employees` table  
- Inserted sample records  
- Ran `SELECT *`, filtered high earners, sorted by salary  

---

## Debugging Log

**Bug — File paths after reorganizing repo**

- Issue: After moving all `.csv` and `.db` files into `/data` and `.py` scripts into `/scripts`, running `visualization.py` failed with `FileNotFoundError` for CSVs and database.  
- Fix: Updated paths in Python scripts to load files from `../data/yourfile.csv` and `../data/database.db`. Charts were saved directly to `/data` to match the new structure.  

*Note:* Before reorganizing, all scripts were running perfectly. This bug was purely due to folder restructuring for GitHub organization.

---

## Output Files & Description

| File | Description |
|---|---|
| `/data/yourfile.csv` | Raw dataset exported from Excel |
| `/data/cleaned_data.csv` | Dataset after Python cleaning and null checks |
| `/data/sample.csv` | Sample dataset used for testing |
| `/data/bar_chart.png` | Bar chart: Average Salary by City |
| `/data/histogram.png` | Histogram: Salary distribution in 5 buckets |
| `/data/database.db` | SQLite database containing `employees` table |
| `/scripts/analysis.py` | Python script for loading and auditing CSV data |
| `/scripts/visualization.py` | Python script generating bar chart and histogram |
| `/scripts/test.py` | Auxiliary testing script from previous tasks |
| `/scripts/queries.sql` | SQL commands for creating table and querying employees |
| `/docs/day3-report.md` | This report documenting all Day 3 tasks |

*Includes some files carried over from Day 2 for continuity.*

---

## Key Insights

- Python allows fast statistical summaries (`df.describe()`) — much quicker than Excel formulas  
- Cleaning data (e.g., numeric conversion of Salary) is crucial  
- Folder structure matters for reproducibility and GitHub organization  
- Visualizations communicate insights clearly without needing raw tables

---

## Status

✅ All four sections completed  
✅ Debugging done after folder restructure  
✅ Charts and cleaned datasets saved in `/data`  
✅ Report complete and ready for GitHub submission