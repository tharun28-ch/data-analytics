from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR.parent / "data" / "bangalore_campaigns.csv"
OUT_FILE  = BASE_DIR.parent / "docs" / "bangalore_marketing_dashboard.png"

# ── Load Data ─────────────────────────────────────────────────────────────────
if not DATA_FILE.exists():
    raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

df = pd.read_csv(DATA_FILE)
print(f"Loaded {len(df)} campaigns from data/bangalore_campaigns.csv")

# ── Forecast (linear regression on Spend vs ROI) ──────────────────────────────
fc_spend = np.linspace(df["Spend"].min(), df["Spend"].max(), 200)
slope, intercept, r_val, _, _ = stats.linregress(df["Spend"], df["ROI_Percentage"])
fc_roi = intercept + slope * fc_spend

# ── Derived Stats for Annotations ─────────────────────────────────────────────
failed_df       = df[df["Status"] == "Failed"]
failed_count    = len(failed_df)
total_lost      = failed_df["Spend"].sum()
best_channel    = df.groupby("Channel")["ROI_Percentage"].mean().idxmax()
worst_channel   = df.groupby("Channel")["ROI_Percentage"].mean().idxmin()
best_roi        = df.groupby("Channel")["ROI_Percentage"].mean().max()

# ── Color Palette ──────────────────────────────────────────────────────────────
ACTIVE_COLOR = "#3498db"
FAILED_COLOR = "#e74c3c"
GRID_COLOR   = "#ecf0f1"
BG_COLOR     = "#f8f9fa"

# ── Figure & Grid ─────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.facecolor":  BG_COLOR,
    "axes.facecolor":    BG_COLOR,
    "axes.edgecolor":    "#cccccc",
    "grid.color":        GRID_COLOR,
    "font.family":       "DejaVu Sans",
})

fig = plt.figure(figsize=(24, 18))
fig.patch.set_facecolor(BG_COLOR)

# ── Title block ───────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.975,
    "Rs. 6,00,000  |  Bangalore Marketing ROI Dashboard",
    fontsize=24, fontweight="bold", ha="center", va="top", color="#1a1a2e",
)
fig.text(
    0.5, 0.955,
    "25 Campaigns across Koramangala, Indiranagar, HSR Layout, Whitefield, JP Nagar & Jayanagar",
    fontsize=13, ha="center", va="top", color="#555555",
)

# ── Layout: 3-row grid (top bar chart spans full width; bottom two side-by-side)
# Rows: row0=bar chart, row1=heatmap+scatter, row2=recommendation
outer = gridspec.GridSpec(
    3, 1,
    height_ratios=[2.2, 2.0, 0.55],
    hspace=0.55,
    top=0.94, bottom=0.04, left=0.06, right=0.97,
)

# ── SUBPLOT 1: Campaign ROI bar chart ─────────────────────────────────────────
ax1 = fig.add_subplot(outer[0])

bar_colors = [FAILED_COLOR if z < -1.0 else ACTIVE_COLOR for z in df["ROI_Z_Score"]]

bars = ax1.bar(
    df["Campaign_ID"], df["ROI_Percentage"],
    color=bar_colors, width=0.65, edgecolor="white", linewidth=0.6,
)

# Value labels above/below each bar
for bar, val in zip(bars, df["ROI_Percentage"]):
    ypos  = bar.get_height() + 8 if val >= 0 else bar.get_height() - 28
    color = "#1a1a2e" if val >= 0 else FAILED_COLOR
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        ypos, f"{val:.0f}%",
        ha="center", va="bottom", fontsize=7.5, color=color, fontweight="bold",
    )

ax1.axhline(0, color="#555555", linewidth=1.2, linestyle="--", zorder=3)
ax1.set_title(
    "Campaign ROI%  |  Z-Score Failure Detection  (red bars = Z < -1.0)",
    fontsize=15, fontweight="bold", pad=12, color="#1a1a2e",
)
ax1.set_xlabel("Campaign ID", fontsize=12, labelpad=8)
ax1.set_ylabel("ROI (%)", fontsize=12, labelpad=8)
ax1.tick_params(axis="x", rotation=45, labelsize=9)
ax1.tick_params(axis="y", labelsize=10)
ax1.set_xlim(-0.6, len(df) - 0.4)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax1.spines[["top", "right"]].set_visible(False)

# Legend patches
ax1.legend(
    handles=[
        mpatches.Patch(color=ACTIVE_COLOR, label="Active / Successful"),
        mpatches.Patch(color=FAILED_COLOR, label=f"Failed  (Z < -1.0)  — {failed_count} campaigns"),
    ],
    loc="upper right", fontsize=10, framealpha=0.85,
)

# ── SUBPLOT 2 & 3: Bottom row ─────────────────────────────────────────────────
bottom_row = gridspec.GridSpecFromSubplotSpec(
    1, 2,
    subplot_spec=outer[1],
    wspace=0.38,
)

# ── SUBPLOT 2: Correlation Heatmap ────────────────────────────────────────────
ax2 = fig.add_subplot(bottom_row[0])

corr_cols   = ["Spend", "Clicks", "Conversions", "Revenue", "ROI_Percentage"]
corr_matrix = df[corr_cols].corr()
corr_labels = ["Spend", "Clicks", "Conv.", "Revenue", "ROI %"]

mask = np.zeros_like(corr_matrix, dtype=bool)   # show full matrix

sns.heatmap(
    corr_matrix,
    annot=True, fmt=".2f",
    cmap="coolwarm", vmin=-1, vmax=1,
    linewidths=1.5, linecolor="white",
    xticklabels=corr_labels, yticklabels=corr_labels,
    annot_kws={"size": 11, "weight": "bold"},
    ax=ax2, cbar_kws={"shrink": 0.75, "pad": 0.02},
)
ax2.set_title(
    "Correlation Heatmap — Key Marketing Metrics",
    fontsize=14, fontweight="bold", pad=12, color="#1a1a2e",
)
ax2.tick_params(axis="x", rotation=30, labelsize=10)
ax2.tick_params(axis="y", rotation=0,  labelsize=10)

# ── SUBPLOT 3: ROI Forecast scatter ───────────────────────────────────────────
ax3 = fig.add_subplot(bottom_row[1])

channel_palette = {
    "Google Ads":            "#3498db",
    "Instagram Ads":         "#e91e63",
    "Facebook Ads":          "#4267B2",
    "LinkedIn Ads":          "#0077b5",
    "Influencer Marketing":  "#9b59b6",
    "Outdoor (Billboards)":  "#e67e22",
}

for channel, grp in df.groupby("Channel"):
    ax3.scatter(
        grp["Spend"], grp["ROI_Percentage"],
        s=grp["Conversions"].clip(lower=10) * 4 + 40,
        color=channel_palette.get(channel, "#888"),
        alpha=0.85, edgecolors="white", linewidth=0.8,
        label=channel, zorder=4,
    )

ax3.plot(fc_spend, fc_roi, color="#e74c3c", linewidth=2, linestyle="--",
         label=f"Trend  (r={r_val:.2f})", zorder=5)

ax3.set_title(
    "ROI Forecast & Channel Effectiveness",
    fontsize=14, fontweight="bold", pad=12, color="#1a1a2e",
)
ax3.set_xlabel("Spend (Rs.)", fontsize=12, labelpad=8)
ax3.set_ylabel("ROI (%)", fontsize=12, labelpad=8)
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))
ax3.spines[["top", "right"]].set_visible(False)
ax3.tick_params(labelsize=10)

ax3.legend(
    loc="upper right", fontsize=9, framealpha=0.85,
    title="Channel", title_fontsize=9,
)

# ── RECOMMENDATION BOX (row 2) ────────────────────────────────────────────────
ax_rec = fig.add_subplot(outer[2])
ax_rec.axis("off")

rec_lines = [
    f"  STRATEGIC RECOMMENDATIONS",
    f"  1. Cut Losses   |  {failed_count} campaigns failed (Z < -1.0) — Rs. {total_lost:,.0f} at risk. Reallocate budget immediately.",
    f"  2. Scale Up     |  '{best_channel}' leads with avg ROI of {best_roi:.0f}%. Increase its allocation.",
    f"  3. Investigate  |  '{worst_channel}' is the worst-performing channel. Audit creatives & targeting.",
    f"  4. Data Signal  |  Check heatmap: Conversions drive Revenue far more than raw Click volume.",
]
rec_text = "\n".join(rec_lines)

ax_rec.text(
    0.5, 0.5, rec_text,
    transform=ax_rec.transAxes,
    fontsize=11.5, fontweight="bold", family="monospace",
    va="center", ha="center",
    color="#1a1a2e",
    bbox=dict(
        boxstyle="round,pad=0.8",
        facecolor="#fff9c4", edgecolor="#f39c12",
        linewidth=2, alpha=0.95,
    ),
)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_FILE, dpi=200, bbox_inches="tight", facecolor=BG_COLOR)
print(f"Dashboard saved to: docs/bangalore_marketing_dashboard.png")
