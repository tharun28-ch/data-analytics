import pandas as pd
import matplotlib.pyplot as plt

# LOAD DATA
df = pd.read_csv("../data/yourfile.csv")

# 🔧 CLEAN SALARY COLUMN
df["Salary"] = df["Salary"].replace('[^0-9]', '', regex=True)  # remove symbols
df["Salary"] = pd.to_numeric(df["Salary"])  # convert to numbers

# BAR CHART
df.groupby("City")["Salary"].mean().plot(kind='bar')
plt.title("Average Salary by City")
plt.ylabel("Salary")
plt.savefig("../data/bar_chart.png")
plt.clf()

# HISTOGRAM
df["Salary"].plot(kind='hist', bins=5)
plt.title("Salary Distribution")
plt.savefig("../data/histogram.png")
plt.clf()