import pandas as pd
import numpy as np
df = pd.read_csv("../data/c_yourfile.csv")

avg_sal = df["Salary"].mean()
df["Category"] = np.where(df["Salary"] > avg_sal, "Above Average", "Below Average")
print("Categorized Dataset:\n", df[["Name", "Salary", "Category"]])