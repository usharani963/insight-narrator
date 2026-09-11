# 🌾 InsightNarrator: Automated Statistical Insight & Narrative Generation Engine

An end-to-end analytics pipeline that combines SQL-based data storage, rigorous statistical hypothesis testing, and a locally hosted LLM to auto-generate plain-English explanations of agricultural yield trends — built to bridge quantitative analysis and non-technical communication.

---

## Problem Statement

Most data analysis stops at a chart or a p-value that only a technical audience can interpret. InsightNarrator automates the next step: it runs proper statistical tests on crop yield data and uses an LLM to translate the results into a clear, business-readable explanation — the way a junior analyst would summarize findings for a non-technical stakeholder.

---

## Dataset

Crop production dataset with the following columns:

`Crop, Crop_Year, Season, State, Area, Production, Annual_Rainfall, Fertilizer, Pesticide, Yield`

Source: publicly available Indian crop yield dataset (1997–2020).

---

## Architecture

```
Raw CSV
   │
   ▼
MySQL (structured storage, SQL aggregation queries)
   │
   ▼
Python: Pandas (cleaning, outlier removal, feature engineering)
   │
   ▼
Statistical Testing Layer (SciPy / Statsmodels / pymannkendall)
   │
   ▼
Visualization Layer (Matplotlib / Seaborn)
   │
   ▼
LangChain + Ollama (local LLM) → narrative generation + causal-language safety filter
   │
   ▼
Streamlit App (interactive Q&A interface)
```

---

## Statistical Tests Implemented

| Question | Test | Why |
|---|---|---|
| Does fertilizer usage affect yield? | Independent t-test (high vs. low fertilizer, split at median) | Compares two groups |
| Does yield differ across states? | One-way ANOVA | Compares 3+ groups |
| Is rainfall correlated with yield? | Pearson correlation | Tests linear relationship |
| Is pesticide usage correlated with yield? | Pearson correlation | Tests linear relationship |
| Has yield changed over time? | Mann-Kendall trend test | Non-parametric trend detection, robust to outliers |
| Are crop type and season independent? | Chi-square test | Tests categorical association |

### Key Methodology Decision: Crop-Normalized Yield

Raw yield values vary enormously by crop type (e.g., sugarcane vs. wheat are on completely different scales). Comparing raw yield across fertilizer groups or states would conflate "which crops are in this group" with "does fertilizer/state matter." To control for this, yield is **z-score normalized within each crop group** before running comparison tests (t-test, ANOVA, trend test), so the statistics reflect genuine group differences rather than crop-mix artifacts.

Outliers were also removed using the IQR method prior to analysis to prevent a small number of extreme values from distorting test results.

---

## LLM Narrative Layer

A locally hosted `llama3.2:1b` model (via Ollama) converts each statistical result into a 2-3 sentence plain-English explanation. Direction and significance are **pre-computed in Python** and passed into the prompt as fixed facts — the LLM is instructed to restate them, not recalculate them.

### Why direction is pre-computed rather than left to the LLM

Initial testing showed the LLM would sometimes state the *opposite* direction of the actual result (e.g., claiming high fertilizer usage was linked to *lower* yield when the data showed the opposite). This is a known limitation of small LLMs — they generate plausible-sounding text rather than performing reliable numeric comparison. Moving the numeric logic into Python and having the LLM only handle phrasing eliminated this failure mode.

---

## Known Limitations

1. **Causal language leakage**: Despite explicit prompt instructions to avoid causal framing (since these are observational correlations, not controlled experiments), the small local LLM occasionally produces phrases like "leads to" or "direct relationship." A regex-based post-processing filter catches and softens common causal phrases, but it is not exhaustive and can occasionally produce slightly awkward sentence grammar after substitution. A production system would use a larger model or a second LLM pass to rewrite flagged sentences fluently.
2. **Scope discipline**: Early testing revealed the LLM would sometimes introduce claims about variables not included in a given test (e.g., mentioning yield in a crop-vs-season independence test that never measured yield). The prompt now explicitly restricts the model to only the named variables.
3. **Model size trade-off**: A 1B-parameter model was used for speed and offline capability. It is less reliable at strict multi-constraint instruction-following than larger models (e.g., `phi3`, `llama3` 8B), which would reduce the above issues further.
4. **Correlational, not causal, findings**: All statistical tests are observational. No causal claims should be drawn from any result without a controlled experiment.

---

## Tech Stack

- **Python**: Pandas, NumPy, SciPy, Statsmodels, pymannkendall
- **Database**: MySQL
- **LLM / NLP**: LangChain, Ollama (locally hosted `llama3.2:1b`)
- **Visualization**: Matplotlib, Seaborn, Power BI
- **App**: Streamlit

---

## Project Structure

```
insight-narrator/
├── data/
│   └── crop_yield_clean.csv
├── load_data.py          # Loads raw CSV into MySQL
├── eda.py                 # Cleaning, outlier removal
├── stats_engine.py        # All statistical test functions
├── visuals.py              # Matplotlib/Seaborn chart functions
├── narrative_engine.py    # LangChain + Ollama narrative generation
├── app.py                  # Streamlit application
├── requirements.txt
└── README.md
```

---

## How to Run Locally

1. Clone the repo and set up a virtual environment:
```bash
git clone https://github.com/YOUR_USERNAME/insight-narrator.git
cd insight-narrator
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

2. Set up MySQL and load the data:
```bash
python load_data.py
python eda.py
```

3. Install [Ollama](https://ollama.com) and pull a model:
```bash
ollama pull llama3.2:1b
```

4. Run the app:
```bash
streamlit run app.py
```

---

## Future Improvements

- Swap the local LLM for a hosted API (e.g., Groq, Together AI) to enable cloud deployment without requiring a local Ollama instance
- Replace regex-based causal-language softening with a second LLM validation pass for more fluent corrections
- Extend to allow free-text questions, with the LLM selecting the appropriate statistical test dynamically
- Add confidence intervals and effect sizes alongside p-values for more complete statistical reporting

---

## Author

Meenuga Usharani
[LinkedIn] | [GitHub] | [Portfolio]
