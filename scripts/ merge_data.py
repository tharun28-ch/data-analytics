import pandas as pd

df_users = pd.read_csv("../data/users.csv")
df_sales = pd.read_csv("../data/sales.csv")

final_report = pd.merge(df_users, df_sales, on="ID", how="inner")
print("Combined Business Report:\n", final_report)
