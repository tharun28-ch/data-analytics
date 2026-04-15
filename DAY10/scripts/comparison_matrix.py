import pandas as pd

# Load data
df = pd.read_csv("../data/sales_cleaned.csv")

# Create a matrix comparing Sales across Regions and Categories
pivot_comparison = df.pivot_table(
    values='Sales',
    index='Region',
    columns='Category',
    aggfunc='sum'
)

# Calculate the percentage difference between two columns if applicable
pivot_comparison['Growth'] = (pivot_comparison['Electronics'] - pivot_comparison['Accessories']) / pivot_comparison['Accessories']

print("Regional Category Performance:")
print(pivot_comparison)
