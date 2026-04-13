import pandas as pd

df = pd.read_csv("data/sales_cleaned.csv")


df['Projected_Rev_High_Price'] = df['Sales'] * 1.15


low_perf_threshold = df['Sales'].quantile(0.25)
underperforming_data = df[df['Sales'] < low_perf_threshold]

print(f"Number of low-performing transactions: {len(underperforming_data)}")
