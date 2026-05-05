import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../data/sales.csv")
# Select only numeric columns for correlation
numeric_df = df.select_dtypes(include=['number'])
correlation_matrix = numeric_df.corr()
# Create a Heatmap
sns.heatmap(correlation_matrix, annot=True, cmap='RdYlGn')
plt.title("Variable Correlation Map")
plt.show()