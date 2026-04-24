import pandas as pd

df = pd.read_csv("../data/meetmux_transactions.csv")
df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'])

latest_date = df['PurchaseDate'].max() + pd.Timedelta(days=1)
rfm = df.groupby('CustomerID').agg({
    'PurchaseDate': lambda x: (latest_date - x.max()).days,
    'CustomerID': 'count',
    'TransactionAmount': 'sum'
})
rfm.columns = ['Recency', 'Frequency', 'Monetary']

rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

print(rfm.head())

rfm['RFM_Segment'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

print("\nAverage Monetary value per segment:")
summary_table = rfm.groupby('RFM_Segment')['Monetary'].mean().reset_index()
print(summary_table)
