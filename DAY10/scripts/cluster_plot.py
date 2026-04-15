import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("../data/sales_cleaned.csv")

plt.figure(figsize=(12, 6))
sns.barplot(x='Region', y='Sales', hue='Category', data=df, estimator=sum)
plt.title("Revenue Comparison: Region vs. Category")
plt.show()
