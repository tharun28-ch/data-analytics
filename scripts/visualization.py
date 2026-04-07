import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("cleaned_data.csv")

# Bar chart
df.groupby("City")["Salary"].mean().plot(kind='bar')
plt.title("Average Salary by City")
plt.show()

# Histogram
df["Salary"].plot(kind='hist', bins=5)
plt.title("Salary Distribution")
plt.show()