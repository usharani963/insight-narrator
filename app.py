# app.py
import streamlit as st
import pandas as pd
from stats_engine import (
    test_fertilizer_effect, test_state_variation,
    test_rainfall_correlation, test_pesticide_correlation,
    test_yearly_trend, test_crop_season_independence
)
from visuals import (
    plot_fertilizer_boxplot, plot_state_variation,
    plot_rainfall_scatter, plot_pesticide_scatter, plot_yearly_trend
)
from narrative_engine import generate_narrative

st.set_page_config(page_title="InsightNarrator", layout="centered")
st.title("🌾 InsightNarrator: Crop Yield Insight Engine")
st.write("Ask a statistical question about crop yield data and get an AI-generated explanation.")

df = pd.read_csv("data/crop_yield_clean.csv")

question = st.selectbox("What do you want to know?", [
    "Does fertilizer usage significantly affect yield?",
    "Does yield differ significantly across states?",
    "Is rainfall correlated with yield?",
    "Is pesticide usage correlated with yield?",
    "Has yield changed significantly over the years?",
    "Are crop type and season independent?"
])

if st.button("Analyze"):
    with st.spinner("Running statistical test..."):
        if question.startswith("Does fertilizer"):
            result = test_fertilizer_effect(df)
            st.pyplot(plot_fertilizer_boxplot(df))
        elif question.startswith("Does yield differ"):
            result = test_state_variation(df)
            st.pyplot(plot_state_variation(df))
        elif question.startswith("Is rainfall"):
            result = test_rainfall_correlation(df)
            st.pyplot(plot_rainfall_scatter(df))
        elif question.startswith("Is pesticide"):
            result = test_pesticide_correlation(df)
            st.pyplot(plot_pesticide_scatter(df))
        elif question.startswith("Has yield changed"):
            result = test_yearly_trend(df)
            st.pyplot(plot_yearly_trend(df))
        else:
            result = test_crop_season_independence(df)

    st.subheader("Statistical Result")
    st.json(result)

    with st.spinner("Generating explanation..."):
        narrative = generate_narrative(result)

    st.subheader("AI-Generated Insight")
    st.write(narrative)