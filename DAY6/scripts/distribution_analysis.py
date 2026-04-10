import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# Load your cleaned sales data
df = pd.read_csv("../data/sales.csv")
# 1. SET THE THEME: Professional look
sns.set_theme(style="whitegrid")
# 2. BOX PLOT: See the spread of sales per Product
plt.figure(figsize=(10, 6))
sns.boxplot(x='productID', y='Sales', data=df, palette='Set2')
plt.title("Sales Distribution per Product (Checking for Outliers)")
plt.show()

# Create a figure with 1 row and 2 columns
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
# Plot 1: Total Sales per Product (Bar Chart)
sns.barplot(ax=axes[0], x='productID', y='Sales', data=df,
estimator=sum)
axes[0].set_title("Total Revenue by Product")
# Plot 2: Sales Trend over Time (Line Chart)
df['Date'] = pd.to_datetime(df['Date'])
daily_sales = df.groupby('Date')['Sales'].sum()
sns.lineplot(ax=axes[1], data=daily_sales)
axes[1].set_title("Daily Sales Velocity")
plt.tight_layout()
plt.show()

# This creates a grid of all numeric relationships
sns.pairplot(df, hue='productID', diag_kind='kde')
plt.show()