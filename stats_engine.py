# stats_engine.py
import pandas as pd
from scipy import stats
import pymannkendall as mk

def add_normalized_yield(df):
    df = df.copy()
    df["yield_z"] = df.groupby("crop")["yield_value"].transform(
        lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
    )
    return df

def test_fertilizer_effect(df):
    df = add_normalized_yield(df)
    median_fert = df["fertilizer"].median()
    high_fert = df[df["fertilizer"] > median_fert]["yield_z"]
    low_fert = df[df["fertilizer"] <= median_fert]["yield_z"]
    t_stat, p_val = stats.ttest_ind(high_fert, low_fert, equal_var=False)
    high_mean, low_mean = high_fert.mean(), low_fert.mean()
    direction = "higher" if high_mean > low_mean else "lower"
    return {
        "test": "Independent t-test",
        "variable": "fertilizer usage vs normalized yield",
        "t_stat": round(float(t_stat), 3),
        "p_value": round(float(p_val), 5),
        "significant": bool(p_val < 0.05),
        "group_means": {
            "high_fertilizer": round(float(high_mean), 3),
            "low_fertilizer": round(float(low_mean), 3)
        },
        "direction": f"High fertilizer usage is associated with {direction} normalized yield compared to low fertilizer usage.",
        "note": "Yield z-normalized within each crop to control for scale differences across crop types."
    }

def test_state_variation(df):
    df = add_normalized_yield(df)
    state_means = df.groupby("state")["yield_z"].mean().sort_values(ascending=False)
    groups = [g["yield_z"].values for _, g in df.groupby("state") if len(g) > 5]
    f_stat, p_val = stats.f_oneway(*groups)
    top_state = state_means.index[0]
    bottom_state = state_means.index[-1]
    return {
        "test": "One-way ANOVA",
        "variable": "state vs normalized yield",
        "f_stat": round(float(f_stat), 3),
        "p_value": round(float(p_val), 5),
        "significant": bool(p_val < 0.05),
        "direction": f"Average normalized yield varies significantly by state — {top_state} has the highest average, {bottom_state} the lowest." if p_val < 0.05 else "No significant difference in average normalized yield was found across states.",
        "note": "Yield z-normalized within each crop to control for scale differences across crop types."
    }

def test_rainfall_correlation(df):
    df = add_normalized_yield(df)
    corr, p_val = stats.pearsonr(df["annual_rainfall"], df["yield_z"])
    direction = "positively" if corr > 0 else "negatively"
    return {
        "test": "Pearson correlation",
        "variable": "rainfall vs normalized yield",
        "correlation": round(float(corr), 3),
        "p_value": round(float(p_val), 5),
        "significant": bool(p_val < 0.05),
        "direction": f"Rainfall is {direction} correlated with normalized yield." if p_val < 0.05 else "No significant correlation was found between rainfall and normalized yield."
    }

def test_pesticide_correlation(df):
    df = add_normalized_yield(df)
    corr, p_val = stats.pearsonr(df["pesticide"], df["yield_z"])
    direction = "positively" if corr > 0 else "negatively"
    return {
        "test": "Pearson correlation",
        "variable": "pesticide vs normalized yield",
        "correlation": round(float(corr), 3),
        "p_value": round(float(p_val), 5),
        "significant": bool(p_val < 0.05),
        "direction": f"Pesticide usage is {direction} correlated with normalized yield." if p_val < 0.05 else "No significant correlation was found between pesticide usage and normalized yield."
    }

def test_yearly_trend(df):
    df = add_normalized_yield(df)
    yearly_avg = df.groupby("crop_year")["yield_z"].mean().sort_index()
    result = mk.original_test(yearly_avg.values)
    return {
        "test": "Mann-Kendall trend test",
        "variable": "year vs normalized yield",
        "trend": result.trend,
        "p_value": round(float(result.p), 5) if result.p > 1e-10 else "< 1e-10",
        "significant": bool(result.p < 0.05),
        "direction": f"Normalized yield shows a significant '{result.trend}' trend over the years." if result.p < 0.05 else "No significant trend in normalized yield was found over the years."
    }
def test_crop_season_independence(df):
    contingency = pd.crosstab(df["crop"], df["season"])
    chi2, p_val, dof, _ = stats.chi2_contingency(contingency)
    return {
        "test": "Chi-square test",
        "variable": "crop vs season",
        "chi2_stat": round(float(chi2), 3),
        "p_value": round(float(p_val), 5) if p_val > 1e-10 else "< 1e-10",
        "significant": bool(p_val < 0.05),
        "direction": "Crop type and season are significantly associated — certain crops are grown predominantly in specific seasons." if p_val < 0.05 else "Crop type and season appear independent of each other."
    }