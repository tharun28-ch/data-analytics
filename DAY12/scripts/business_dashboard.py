import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load data
df = pd.read_csv("../data/sales_cleaned.csv")

# 2. Set up the 2x2 grid
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Executive Business Performance Dashboard', fontsize=20)

# Plot 1: Monthly Sales Trend (Top Left)
sns.lineplot(ax=axes[0, 0], x='Date', y='Sales', data=df)
axes[0, 0].set_title('Sales Trend Over Time')

# Add a note to the Trend plot
axes[0, 0].annotate('Campaign Launch', xy=('2026-03-15', 5000),
             xytext=('2026-03-01', 7000),
             arrowprops=dict(facecolor='black', shrink=0.05))

# Plot 2: Regional Performance (Top Right)
sns.barplot(ax=axes[0, 1], x='Region', y='Sales', data=df, estimator=sum)
axes[0, 1].set_title('Revenue by Region')

# Plot 3: Category Distribution (Bottom Left)
df['Category'].value_counts().plot.pie(ax=axes[1, 0], autopct='%1.1f%%')
axes[1, 0].set_title('Sales Distribution by Category')

# Plot 4: Price vs Sales Correlation (Bottom Right)
sns.scatterplot(ax=axes[1, 1], x='Price', y='Sales', data=df)
axes[1, 1].set_title('Price vs. Sales Volume')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
