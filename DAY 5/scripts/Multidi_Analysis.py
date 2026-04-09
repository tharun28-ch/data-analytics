import pandas as pd
df = pd.read_csv("../data/sales.csv")

pivot = df.pivot_table(values='Sales', index='productID', aggfunc='sum')
pivot.to_csv("../data/products.csv")

print("--- Product Performance Pivot ---")
print(pivot)
