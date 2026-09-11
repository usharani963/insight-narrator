# narrative_engine.py
import re
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

llm = Ollama(model="llama3.2:1b", num_predict=300)


narrative_prompt = PromptTemplate(
    input_variables=["test_name", "variable", "direction", "p_value", "significant"],
    template="""
You are a data analyst writing for a non-technical business audience.

Statistical test performed: {test_name}
Variables analyzed: {variable}
Pre-computed finding (restate this exact sentence, do not reinterpret or contradict it): {direction}
P-value: {p_value}
Statistically significant (p < 0.05): {significant}

Write a 2-3 sentence plain-English explanation. Base your explanation entirely
on the pre-computed finding given above — do not calculate or guess direction yourself.

IMPORTANT RULES:
- Only discuss the exact variables named above.
- This is observational, not experimental — do not imply causation.
- This analysis only covers historical/past data — do not make predictions or claims about future trends.
- Never contradict the "Statistically significant" value given.
- Avoid jargon.
"""
)

CAUSAL_REPLACEMENTS = {
    r"\blead(s)? to\b": "is associated with",
    r"\bcauses?\b": "association with",
    r"\bmakes a difference\b": "shows an association",
    r"\bresults? in\b": "is associated with",
    r"\bactually\b": "",
}
def soften_causal_language(text: str) -> str:
    for pattern, replacement in CAUSAL_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def generate_narrative(result: dict) -> str:
    prompt = narrative_prompt.format(
        test_name=result["test"],
        variable=result["variable"],
        direction=result.get("direction", ""),
        p_value=result["p_value"],
        significant=result["significant"]
    )
    raw_output = llm.invoke(prompt)
    return soften_causal_language(raw_output)