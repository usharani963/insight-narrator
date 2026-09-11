import pandas as pd
from sqlalchemy import create_engine

# 1. Read CSV
df = pd.read_csv("data/crop_yield_raw.csv")

# 2. Clean column names
df.columns = [
    c.strip().lower().replace(" ", "_")
    for c in df.columns
]

# 3. Rename Yield to match MySQL column
df = df.rename(columns={
    "yield": "yield_value"
})

# 4. Remove rows where area or production is missing
df = df.dropna(subset=["production", "area"])

# 5. Remove invalid values
df = df[df["area"] > 0]
df = df[df["production"] >= 0]

# 6. Connect to MySQL
engine = create_engine(
    "mysql+mysqlconnector://root:usha12@localhost/insight_narrator"
)

# 7. Load data into MySQL
df.to_sql(
    "crop_yield",
    con=engine,
    if_exists="append",
    index=False
)

print(f"Loaded {len(df)} rows into MySQL.")