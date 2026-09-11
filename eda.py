# eda.py
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqlconnector://root:usha12@localhost/insight_narrator")
df = pd.read_sql("SELECT * FROM crop_yield", con=engine)

# # Feature engineering
# df["yield"] = df["production"] / df["area"]
# in eda.py, remove or comment out the manual calculation:
# df["yield"] = df["production"] / df["area"]   # not needed — already in the dataset

# instead just rename for consistency with stats_engine.py:
df = df.rename(columns={"yield": "yield_value"})
df = df.drop(columns=["yield"], errors="ignore")  # drop if duplicate still exists

# Basic checks
print(df.info())
print(df.describe())
print(df.isnull().sum())

# Drop outliers using IQR
# Apply this BEFORE saving the clean CSV — confirm it's actually executing
Q1, Q3 = df["yield_value"].quantile(0.25), df["yield_value"].quantile(0.75)
IQR = Q3 - Q1
before = len(df)
df = df[(df["yield_value"] >= Q1 - 1.5*IQR) & (df["yield_value"] <= Q3 + 1.5*IQR)]
print(f"Removed {before - len(df)} outlier rows out of {before}")

df.to_csv("data/crop_yield_clean.csv", index=False)