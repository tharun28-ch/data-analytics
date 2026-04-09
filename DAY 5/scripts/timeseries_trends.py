import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("../data/sales.csv")

df['Date'] = pd.to_datetime(df['Date'])
# 1. SET INDEX: Make the date the index for easy slicing
df.set_index('Date', inplace=True)
# 2. RESAMPLE: Aggregate sales by Week ('W') or Month ('M')
weekly_sales = df['Sales'].resample('W').sum()
print("Weekly Sales Performance:\n", weekly_sales)
# 3. VISUALIZE: The Trend Line
weekly_sales.plot(kind='line', marker='o', color='teal')
plt.title("Weekly Revenue Trend")
plt.ylabel("Total Sales ($)")
plt.show()