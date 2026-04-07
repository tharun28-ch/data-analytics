import pandas as pd

df = pd.read_csv("yourfile.csv")

# Cleaning
df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
df = df.dropna()

# Save cleaned data
df.to_csv("cleaned_data.csv", index=False)