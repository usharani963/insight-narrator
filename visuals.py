# visuals.py
import matplotlib.pyplot as plt
import seaborn as sns
from stats_engine import add_normalized_yield

def plot_fertilizer_boxplot(df):
    df = add_normalized_yield(df)
    median_fert = df["fertilizer"].median()
    df["fertilizer_group"] = df["fertilizer"].apply(
        lambda x: "High" if x > median_fert else "Low"
    )
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=df, x="fertilizer_group", y="yield_z", ax=ax)
    ax.set_title("Normalized Yield: High vs Low Fertilizer Usage")
    ax.set_ylabel("Yield (z-score, normalized within crop)")
    return fig

def plot_state_variation(df):
    df = add_normalized_yield(df)
    top_states = df.groupby("state")["yield_z"].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(x=top_states.values, y=top_states.index, ax=ax)
    ax.set_title("Top 10 States by Average Normalized Yield")
    ax.set_xlabel("Average Yield (z-score, normalized within crop)")
    return fig

def plot_rainfall_scatter(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.regplot(data=df, x="annual_rainfall", y="yield_value", ax=ax, scatter_kws={"alpha": 0.4})
    ax.set_title("Rainfall vs Yield (raw values)")
    return fig

def plot_pesticide_scatter(df):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.regplot(data=df, x="pesticide", y="yield_value", ax=ax, scatter_kws={"alpha": 0.4}, color="orange")
    ax.set_title("Pesticide Usage vs Yield (raw values)")
    return fig

def plot_yearly_trend(df):
    df = add_normalized_yield(df)
    yearly_avg = df.groupby("crop_year")["yield_z"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.lineplot(data=yearly_avg, x="crop_year", y="yield_z", marker="o", ax=ax)
    ax.set_title("Average Normalized Yield Over Years")
    ax.set_ylabel("Yield (z-score, normalized within crop)")
    return fig