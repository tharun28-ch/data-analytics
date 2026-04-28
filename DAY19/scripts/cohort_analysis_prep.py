import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("meetmux_transactions.csv")
df["PurchaseDate"] = pd.to_datetime(df["PurchaseDate"])

df["OrderMonth"] = df["PurchaseDate"].dt.to_period("M")
df["CohortMonth"] = (
    df.groupby("CustomerID")["PurchaseDate"].transform("min").dt.to_period("M")
)


def get_date_int(df, column):
    year = df[column].dt.year
    month = df[column].dt.month
    return year, month


order_year, order_month = get_date_int(df, "OrderMonth")
cohort_year, cohort_month = get_date_int(df, "CohortMonth")

years_diff = order_year - cohort_year
months_diff = order_month - cohort_month

df["CohortIndex"] = years_diff * 12 + months_diff + 1
print(df[["CustomerID", "CohortMonth", "CohortIndex"]].head())
