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

| Question                                  | Test                                                          | Why                                                |
| ----------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------- |
| Does fertilizer usage affect yield?       | Independent t-test (high vs. low fertilizer, split at median) | Compares two groups                                |
| Does yield differ across states?          | One-way ANOVA                                                 | Compares 3+ groups                                 |
| Is rainfall correlated with yield?        | Pearson correlation                                           | Tests linear relationship                          |
| Is pesticide usage correlated with yield? | Pearson correlation                                           | Tests linear relationship                          |
| Has yield changed over time?              | Mann-Kendall trend test                                       | Non-parametric trend detection, robust to outliers |
| Are crop type and season independent?     | Chi-square test                                               | Tests categorical association                      |

### Key Methodology Decision: Crop-Normalized Yield

Raw yield values vary enormously by crop type (e.g., sugarcane vs. wheat are on completely different scales). Comparing raw yield across fertilizer groups or states would conflate "which crops are in this group" with "does fertilizer/state matter." To control for this, yield is **z-score normalized within each crop group** before running comparison tests (t-test, ANOVA, trend test), so the statistics reflect genuine group differences rather than crop-mix artifacts.

Outliers were also removed using the IQR method prior to analysis to prevent a small number of extreme values from distorting test results.

---

## LLM Narrative Layer

Each statistical result is converted into a 2-3 sentence plain-English explanation by an LLM. Direction and significance are **pre-computed in Python** and passed into the prompt as fixed facts — the LLM is instructed to restate them, not recalculate them.

### Why direction is pre-computed rather than left to the LLM

Initial testing (with a local model) showed the LLM would sometimes state the _opposite_ direction of the actual result (e.g., claiming high fertilizer usage was linked to _lower_ yield when the data showed the opposite). This is a known limitation of small LLMs — they generate plausible-sounding text rather than performing reliable numeric comparison. Moving the numeric logic into Python and having the LLM only handle phrasing eliminated this failure mode entirely, regardless of which model is used downstream.

### Model Comparison

Three models were tested for the narrative generation step, run against the identical prompt and pre-computed findings:

| Model                            | Hosting | Params | Observed behavior                                                                                                                                                                                                                                                   |
| -------------------------------- | ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `llama3.2:1b` (Ollama)           | Local   | 1B     | Frequently misstated numeric direction, introduced claims about untested variables (scope creep), and used causal language despite explicit prompt constraints. Required additional safeguards to be usable.                                                        |
| `llama-3.3-70b-versatile` (Groq) | Hosted  | 70B    | Correct direction, correct significance framing, properly hedged (correlational, not causal) language — no safety-net corrections needed.                                                                                                                           |
| `openai/gpt-oss-20b` (Groq)      | Hosted  | 20B    | **Final choice.** Matched the 70B model's reliability on direction, significance, and scope — with faster response times and a more generous free tier. Occasional grammar softening around the causal-language filter (see below), but no factual errors observed. |

The project ships with `openai/gpt-oss-20b` via the Groq API as the default, since it offered the best balance of reliability, speed, and cost for this use case. The code is structured so swapping models (or switching back to a local Ollama model for offline use) requires changing only one line in `narrative_engine.py`.

---

## Known Limitations

1. **Causal language leakage (regex filter)**: Even with hosted models, a regex-based post-processing filter is kept in place as a safety net to catch and soften causal phrases (e.g., "causes" → "association with"), since prompt instructions alone are not a guaranteed constraint. Because this is a word-level substitution rather than a grammar-aware rewrite, it can occasionally produce a slightly awkward sentence (e.g., "does not imply that pesticides association with higher yields" instead of a fully fluent rewrite). A production system would use a second LLM pass to rewrite flagged sentences fluently instead of direct word substitution.
2. **Scope discipline**: Early testing with a small local model revealed the LLM would sometimes introduce claims about variables not included in a given test (e.g., mentioning yield in a crop-vs-season independence test that never measured yield). The prompt now explicitly restricts the model to only the named variables, and this failure mode was not observed with the larger hosted models used in the final version.
3. **Model size trade-off**: Smaller/local models are far less reliable at strict multi-constraint instruction-following (numeric direction, scope, causal framing) than larger hosted models — see the Model Comparison table above for the specific failure modes observed at each scale.
4. **Correlational, not causal, findings**: All statistical tests are observational. No causal claims should be drawn from any result without a controlled experiment.

---

## Sample Output

**Question**: Does fertilizer usage significantly affect yield?

```json
{
  "test": "Independent t-test",
  "variable": "fertilizer usage vs normalized yield",
  "t_stat": 2.509,
  "p_value": 0.0121,
  "significant": true,
  "group_means": {
    "high_fertilizer": 0.019,
    "low_fertilizer": -0.019
  },
  "direction": "High fertilizer usage is associated with higher normalized yield compared to low fertilizer usage.",
  "note": "Yield z-normalized within each crop to control for scale differences across crop types."
}
```

**AI-Generated Insight**:

> The analysis shows that farms with higher fertilizer usage tend to have higher normalized yield than those with lower usage. The difference is statistically significant, with a p-value of 0.0121, indicating that the observed association is unlikely to be due to random chance.

**Question**: Is rainfall correlated with yield?

```json
{
  "test": "Pearson correlation",
  "variable": "rainfall vs normalized yield",
  "correlation": 0.002,
  "p_value": 0.77784,
  "significant": false,
  "direction": "No significant correlation was found between rainfall and normalized yield."
}
```

**AI-Generated Insight**:

> No correlation between rainfall and the yield of a crop was found through statistical analysis. The results show that the amount of rainfall in a given area does not have a significant effect on the yield of that crop.

---

## Tech Stack

- **Python**: Pandas, NumPy, SciPy, Statsmodels, pymannkendall
- **Database**: MySQL
- **LLM / NLP**: LangChain, Groq API (`openai/gpt-oss-20b`) — swappable for a local Ollama model for fully offline use
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

3. Get a free API key from [Groq Console](https://console.groq.com), then create a `.env` file in the project root (see `.env.example`):

```
GROQ_API_KEY=your_actual_key_here
```

4. Run the app:

```bash
streamlit run app.py
```

**Optional — fully offline mode**: install [Ollama](https://ollama.com), pull a local model (`ollama pull llama3.2:1b`), and swap the model initialization in `narrative_engine.py` from `ChatGroq` to `Ollama`. Note: local small models are less reliable at following the narrative constraints — see Model Comparison above.

---

## Future Improvements

- Swap the local LLM for a hosted API (e.g., Groq, Together AI) to enable cloud deployment without requiring a local Ollama instance
- Replace regex-based causal-language softening with a second LLM validation pass for more fluent corrections
- Extend to allow free-text questions, with the LLM selecting the appropriate statistical test dynamically
- Add confidence intervals and effect sizes alongside p-values for more complete statistical reporting

---

## Author

Meenuga Usharani
[https://www.linkedin.com/in/meenugausharani963/] | [https://github.com/usharani963] | [https://meenuga-portfolio.vercel.app/]
