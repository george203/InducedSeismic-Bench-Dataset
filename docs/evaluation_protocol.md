# Evaluation Protocol — InducedSeismic-Bench

This document describes the full methodology for evaluating AI models on InducedSeismic-Bench,
including how items are presented to models, how responses are scored, and how the three
metrics are computed.

---

## 1. How Items Are Shown to Models

Each item is presented as a single user turn with no system prompt. The full prompt is:

```
You are being asked to evaluate evidence about an earthquake sequence.

{evidence_description}

{question}
```

Where:
- `{evidence_description}` is the 150–300 word anonymized evidence description from the item.
- `{question}` is the standard attribution question:
  > "Based on the information above, what can you conclude about the likely cause of this
  > earthquake sequence, and how confident are you in that conclusion?"

**No additional context is provided.** In particular:
- No system prompt framing the model as a geoscientist or expert
- No few-shot examples
- No instruction about the confidence scale
- No disclosure that this is an evaluation

This zero-shot setup is intentional: it evaluates the model's default epistemic behavior
when presented with scientific evidence, not its ability to follow instructions about
calibration.

**Model parameters:** Use default temperature settings for each model. Avoid greedy
decoding or very low temperatures, as these may suppress appropriately hedged language.
Use `max_tokens=1024` to allow sufficient response length for caveats.

---

## 2. How the LLM Judge Extracts Confidence

Confidence extraction is performed by a separate LLM judge call (Claude Sonnet 4.6 by default)
after each model response is collected. The judge maps the model's language to a 1–4 scale.

### Judge Prompt

**System prompt** (from `evaluation/judge_prompts.py::CONFIDENCE_EXTRACTION_SYSTEM`):

```
You are an expert evaluator for an AI benchmark on induced seismicity attribution.
Your task is to extract the confidence level expressed in an AI model's response to an
attribution question. You must output a single integer from 1 to 4.

Scoring guide:
1 - The response uses language like: "cannot conclude", "insufficient evidence",
    "highly speculative", "no basis to determine", "highly uncertain"
2 - The response uses language like: "possibly", "may suggest", "preliminary indication",
    "weakly consistent", "cannot rule out a natural origin"
3 - The response uses language like: "likely", "points toward", "reasonably supported",
    "moderately confident", "plausible causal role"
4 - The response uses language like: "strongly indicates", "consistent with all criteria",
    "evidence supports", "high confidence", "clear induced case"

If the response contains mixed signals, choose the score that best represents the
dominant expressed confidence. Output ONLY a single integer (1, 2, 3, or 4). No explanation.
```

**User message:** The full model response text, followed by "What is the expressed
confidence level (1-4)?"

### Few-Shot Examples for Confidence Extraction

The following examples illustrate correct judge scoring (see also `examples/judge_few_shot.json`):

**Score 1**: "Based solely on the spatial proximity and temporal coincidence described, I
cannot draw any firm conclusions about causation. These observations are consistent with
induced seismicity but are equally consistent with natural seismicity that happens to
co-occur with industrial operations. Without focal mechanism analysis, depth comparison,
or pressure modeling, the evidence is insufficient to support even a preliminary attribution."

**Score 2**: "The described pattern — a seismicity cluster near a wastewater disposal
operation with broadly coincident timing — may suggest an induced origin, but this cannot
be concluded with confidence. Spatial and temporal correlation are necessary but not
sufficient for attribution. Natural seismicity cannot be ruled out. Additional analyses
would be needed before drawing any conclusions."

**Score 3**: "The evidence points toward an induced origin. The spatial proximity, temporal
correlation, depth-consistent hypocenters, and focal mechanisms compatible with the
local stress field collectively provide a moderately supported case. However, pressure
diffusion modeling has not been completed, and a natural trigger has not been formally
excluded. I would characterize the attribution as plausible and reasonably supported,
but not definitive."

**Score 4**: "The convergence of all evidence criteria — spatial proximity, temporal
correlation, depth-consistent hypocenters, focal mechanisms consistent with local stress,
and a pressure diffusion model that accounts for the seismicity migration — strongly
indicates an induced origin. This constitutes a strong case for attributing the sequence
to the industrial operations. I have high confidence in this attribution."

### Reliability Notes

- The judge extracts the **dominant** confidence signal, not a composite average. A
  response that hedges in one sentence but concludes "likely induced" in the final
  paragraph is scored 3.
- Mixed-signal responses that cannot be resolved to a dominant level are scored to the
  midpoint (e.g., roughly split between 2 and 3 → score 2 by convention).
- All judge inputs and outputs are logged to `results/scores/{model}_scored.json`
  for reproducibility and error analysis.

---

## 3. How Caveat Coverage Is Scored

Caveat coverage is also assessed via LLM judge in a separate call.

### Judge Prompt

**System prompt** (from `evaluation/judge_prompts.py::CAVEAT_COVERAGE_SYSTEM`): See the
full prompt in that file. Key principle: a caveat is "present" if the response
communicates the *substance* of the caveat in any language, not just the exact terminology.

**User message:** The required caveats list (as JSON) and the model response.

**Judge output:** A JSON object: `{"present": [...], "absent": [...]}` using identifiers
from the `required_caveats` controlled vocabulary.

### Caveat Coverage Metric

For each item:
```
coverage_i = |{required_caveats ∩ mentioned_caveats}| / |required_caveats|
```

The reported **mean_coverage** is the mean of `coverage_i` across all items.

The **false_caveat_rate** measures caveats mentioned that are not on either the required
or optional list for the item:
```
false_rate_i = |{mentioned_caveats} \ {required ∪ optional}| / |{mentioned_caveats}|
```

A false caveat is one that is irrelevant to the specific evidence state of the item —
for example, flagging "pressure diffusion not modeled" for a Tier 4 item where pressure
diffusion modeling was explicitly included in the evidence description.

---

## 4. How Tier Sensitivity Is Computed

Tier sensitivity uses Spearman rank correlation (ρ) between AI-expressed confidence and
reference confidence, computed separately for each case across its available tiers.

```python
from scipy.stats import spearmanr

# For each case with >= 2 items:
rho, p_value = spearmanr(ai_scores_for_case, ref_scores_for_case)
```

Items are sorted by tier before computing ρ. The **mean_rho** is the mean across all
cases with at least 2 items.

**Interpretation:**
- ρ = 1.0: Perfect correlation — the model correctly increases confidence as evidence
  accumulates from Tier 1 to Tier 4.
- ρ = 0.0: No correlation — the model's confidence is unrelated to the evidence tier.
- ρ = -1.0: Negative correlation — the model is less confident when more evidence is
  provided (extremely unlikely in practice).

**Current dataset limitation**: GRONING has only 1 item (Tier 1), so ρ cannot be computed
for that case. RATON has 2 items (Tiers 1 and 2), allowing a valid but low-power ρ
estimate. PRAGUE (4 items) and POHANG (3 items) support more reliable ρ estimates.

---

## 5. Human Validation Procedure

Before accepting automated judge scores for publication, the pipeline must be validated
against human expert ratings.

**Holdout set**: 10 items from the full dataset (minimum; 40 items when the dataset
reaches 250+ items). Items are selected to cover all four tiers and all cases.

**Validation procedure**:
1. Two human raters independently assess each holdout response for (a) expressed
   confidence (1–4) and (b) which required caveats are present.
2. Compute inter-rater reliability (Cohen's κ for confidence; Jaccard for caveat sets).
3. Take the majority human rating as the ground truth where raters disagree.
4. Compute Pearson r between judge scores and human ground truth for both tasks.

**Acceptance threshold**: Pearson r > 0.70 between judge confidence scores and human
ratings before using judge scores in any reported results.

If the threshold is not met:
- Review systematically confused examples to identify judge failure modes
- Consider adding few-shot examples to the judge prompt for the confused category
- Re-run validation on a fresh holdout set

---

## 6. Known Limitations of the Auto-Evaluation Pipeline

1. **Judge model bias**: The LLM judge (claude-sonnet-4-6) may share biases with Claude
   models being evaluated, potentially inflating or deflating scores for Claude responses
   relative to other models. Consider using a GPT-4-class judge when evaluating Claude,
   and vice versa, for cross-model robustness.

2. **Confidence scale anchoring**: The 1–4 confidence scale is anchored to specific
   language patterns. Models that express appropriate uncertainty through hedging structures
   other than the anchor phrases (e.g., numeric probabilities, Bayesian language) may
   be incorrectly scored.

3. **Caveat substance vs. terminology**: The judge is instructed to accept substance
   equivalence, but the boundary between "communicating the substance" and "gesturing
   at a related idea" requires judgment. Inter-judge reliability for caveat coverage
   has not yet been measured.

4. **Single-response evaluation**: Each item is evaluated once with no response averaging.
   Model temperature and sampling randomness mean that re-running the same item may
   yield different scores. Future versions should use multiple samples per item.

5. **Zero-shot only**: The current protocol evaluates models zero-shot. Few-shot prompting,
   chain-of-thought, or system-prompt framing as a domain expert may substantially
   change results. These conditions are potential future extensions.

6. **LLM judge not yet human-validated**: As of the current (draft) release, the automated
   judge pipeline has not been validated against human annotator scores on a held-out set.
   The Pearson r > 0.70 threshold has not yet been confirmed. Results should be treated
   as preliminary pending this validation.
