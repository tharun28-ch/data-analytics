import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/c_yourfile.csv")

city_stats = df.groupby("City")["Salary"].mean()
print("Average Salary by City:\n", city_stats)

pivot = df.pivot_table(values="Salary", index="City", columns="Age", aggfunc="mean")
print("\nData Pivot Table:\n", pivot)

city_stats.plot(kind='pie', autopct='%1.1f%%')
plt.show()