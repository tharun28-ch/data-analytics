import pandas as pd

df = pd.read_csv("data/sales_cleaned.csv")


top_performers = df.groupby('Product')['Sales'].sum().nlargest(5)


total_rev = df['Sales'].sum()
contribution_pct = (top_performers.sum() / total_rev) * 100

print(f"Top 5 Products contribute {contribution_pct:.2f}% of total revenue.")
