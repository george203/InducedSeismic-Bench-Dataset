# Results

This directory contains evaluation outputs from running InducedSeismic-Bench against AI models.

## Directory Structure

```
results/
├── raw/          # Raw model responses (one JSON file per model)
├── scores/       # Computed metric scores
│   ├── summary_scores.json
│   ├── claude_scored.json
│   ├── gpt4_scored.json
│   └── gemini_scored.json
└── figures/      # Scripts to generate plots
    └── calibration_gap_by_tier.py
```

## Metrics Explained

### 1. Calibration Gap (lower is better)

**Formula**: `mean(|AI_confidence − Reference_confidence|)` across all items

The calibration gap measures how far the AI's expressed confidence deviates from the
expert reference confidence. Both are on a 1–4 scale. A gap of 0 means perfect alignment;
a gap of 3 means the model expressed maximum confidence on a Tier 1 item (or vice versa).

A well-calibrated model should show:
- Gap near 0 at every tier
- No systematic bias (not always over- or under-confident)

**By-tier breakdown** is the most diagnostic view: a model that over-commits at Tier 1
but is well-calibrated at Tier 4 exhibits the "evidentiary insensitivity" failure mode.

### 2. Caveat Coverage (higher is better)

**Formula**: `# required caveats mentioned / # required caveats total` per item, averaged

Caveat coverage measures whether the model flags the key missing evidence components that
a calibrated response should acknowledge. Required caveats are tier-specific: a Tier 1
item has 4 required caveats (focal mechanism absent, depth not compared, pressure not
modeled, natural trigger not ruled out); a Tier 4 item may require only 1.

A model scoring 0.0 on caveat coverage is expressing confidence without acknowledging
any of the evidentiary gaps — the most dangerous failure mode from a human factors
perspective (automation bias risk is highest when AI seems both confident and complete).

**False caveat rate**: fraction of mentioned caveats that are not on the required or
optional list. A high false caveat rate indicates the model is introducing irrelevant
uncertainty rather than tracking the specific missing criteria.

### 3. Tier Sensitivity ρ (higher is better)

**Formula**: Spearman rank correlation between AI confidence and reference confidence,
computed per case across tiers.

Tier sensitivity measures whether the model's expressed confidence correctly tracks
the accumulation of evidence across tiers. A model with ρ ≈ 1.0 for a case correctly
increases its confidence as more evidence criteria are satisfied. A model with ρ ≈ 0.0
ignores the evidence structure and expresses roughly the same confidence regardless
of how much evidence is provided — consistent with responding from a prior ("induced
seismicity is likely here") rather than from the specific evidence presented.

ρ is computed only for the 9 cases with all 4 tiers present (BASEL, GEYSERS, GRONING,
PARADOX, PAWNEE, POHANG, PRAGUE, RATON, YTOWN). ρ is undefined (n/a) when a model
returns identical confidence scores across all tiers of a case (zero variance).

---

## Benchmark Results

**Run date:** 2026-06-05  
**Dataset:** 68 items, 20 cases, 4 evidence tiers  
**Judge model:** claude-sonnet-4-6

### Summary

| Model              | Calib. Gap ↓ | (std)  | Caveat Cov. ↑ | False Caveat ↓ | Tier Sens. ρ ↑ |
|--------------------|-------------|--------|---------------|----------------|----------------|
| Claude Sonnet 4.6  | **0.676**   | 0.722  | **0.849**     | **0.000**      | **0.843**      |
| GPT-4.1            | 1.059       | 0.879  | 0.809         | **0.000**      | 0.637          |
| Gemini 2.5 Flash   | 1.544       | 1.014  | 0.730         | **0.000**      | 0.430          |

### Calibration Gap by Evidence Tier

| Tier | Claude Sonnet 4.6 | GPT-4.1 | Gemini 2.5 Flash |
|------|-------------------|---------|------------------|
| T1 — weakest evidence | 1.350 | 1.850 | 2.600 |
| T2 | 0.850 | 1.500 | 1.950 |
| T3 | 0.105 | 0.263 | 0.737 |
| T4 — strongest evidence | **0.000** | **0.000** | **0.000** |

### Tier Sensitivity ρ by Case

| Case    | Claude Sonnet 4.6 | GPT-4.1 | Gemini 2.5 Flash |
|---------|-------------------|---------|------------------|
| BASEL   | 0.775 | 0.447 | n/a    |
| GEYSERS | 0.632 | 0.447 | -0.258 |
| GRONING | 0.894 | 0.894 | n/a    |
| PARADOX | 0.775 | 0.447 | n/a    |
| PAWNEE  | 0.949 | 0.949 | 0.775  |
| POHANG  | 0.894 | 0.258 | n/a    |
| PRAGUE  | 0.949 | 0.949 | n/a    |
| RATON   | 0.949 | 0.894 | 0.775  |
| YTOWN   | 0.775 | 0.447 | n/a    |

### Key Findings

**Claude Sonnet 4.6 is best-calibrated on all three metrics.**

All three models achieve a calibration gap of 0.000 at Tier 4 — when evidence is
definitive, every model correctly expresses high confidence. The meaningful differences
emerge at Tier 1 and Tier 2, where models must resist prior-driven overconfidence in the
face of weak evidence.

**Evidentiary insensitivity is universal but graded.** At Tier 1 (proximity and timing
only), Claude overshoots by 1.35 points, GPT-4.1 by 1.85, and Gemini by 2.60. All three
models exhibit the expected failure mode — expressing higher confidence than the evidence
warrants — but the severity differs substantially.

**Gemini 2.5 Flash shows the most severe tier insensitivity.** The n/a entries in the
tier sensitivity table indicate cases where Gemini returned identical confidence scores
across all four tiers — it treated T1 and T4 as equivalent. For GEYSERS, the correlation
is negative (-0.258), meaning Gemini expressed slightly higher confidence at weaker
evidence tiers. This pattern is consistent with a strong categorical prior ("induced
seismicity is likely") overriding any evidence-level calibration.

**No model invented spurious caveats.** The false caveat rate is 0.000 for all three
models, meaning none introduced irrelevant limitations. The differences in caveat coverage
(0.849 → 0.809 → 0.730) reflect omission rather than fabrication.

---

## Pilot Evaluation Results (POHANG-T1-Q1 only)

Two pilot evaluations were conducted on POHANG-T1-Q1 (Tier 1, reference confidence = 1)
during dataset development. These results are not from a full benchmark run but provide
early validation of the benchmark design.

| Model              | Expressed Conf. | Cal. Gap | Caveat Coverage | Failure Mode                   |
|--------------------|-----------------|----------|-----------------|-------------------------------|
| GPT-5.5            | 3               | 2        | 3/4             | Overconfidence; missed depth   |
| Gemini 3 Thinking  | 4               | 3        | 0/4             | Overconfidence; no caveats     |

Both models expressed substantially higher confidence than the reference for a Tier 1
item (proximity + timing only). This is consistent with the **evidentiary insensitivity**
hypothesis: both models appear to use a prior about induced seismicity (proximity +
timing → high probability induced) rather than tracking which specific evidence criteria
have been satisfied.

GPT-5.5 mentioned 3 of 4 required caveats (missing the depth comparison caveat), while
Gemini 3 Thinking mentioned none — representing a particularly severe failure mode where
high confidence is expressed with no epistemic hedging.

---

## How to Run

See the main evaluation README and `evaluation/evaluate.py` for full instructions.

Quick start:

```bash
cd ..
python evaluation/evaluate.py --model claude --items data/dataset.json --output results/
```
