import pandas as pd
import numpy as np

# 1. Load data
df = pd.read_csv("../data/sales_cleaned.csv")

# 2. Calculate Z-Score for Sales
# Z = (Value - Mean) / Standard Deviation
df['z_score'] = (df['Sales'] - df['Sales'].mean()) / df['Sales'].std()

# 3. Identify Outliers (Usually anything > 3 or < -3)
outliers = df[np.abs(df['z_score']) > 3]

print(f"Detected {len(outliers)} outliers in the dataset.")
print(outliers[['Date', 'Product', 'Sales', 'z_score']])
