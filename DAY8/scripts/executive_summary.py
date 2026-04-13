import pandas as pd

df = pd.read_csv("data/sales_cleaned.csv")

summary = df.groupby(['Product', 'Date']).agg({
    'Sales': ['sum', 'count'],
    'Quantity': 'mean'
})


summary.columns = ['Total_Revenue', 'Transaction_Count', 'Avg_Qty_Per_Order']

print("Executive Deep-Dive:")
print(summary.head(10))
