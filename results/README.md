# Results

This directory contains evaluation outputs from running InducedSeismic-Bench against AI models.

## Directory Structure

```
results/
├── raw/          # Raw model responses (one JSON file per model)
├── scores/       # Computed metric scores
│   └── summary_scores.json
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

ρ is undefined for cases with only one item in the dataset; it requires at least 2 tiers.

---

## Results Table

Results below are from the full benchmark run. Items marked TBD await evaluation.

| Model              | Calibration Gap ↓ | Caveat Coverage ↑ | Tier Sensitivity ρ ↑ |
|--------------------|-------------------|-------------------|----------------------|
| GPT-4.1            | TBD               | TBD               | TBD                  |
| Claude Sonnet 4.6  | TBD               | TBD               | TBD                  |
| Gemini 2.0 Flash   | TBD               | TBD               | TBD                  |
| Llama 3.1 70B      | TBD               | TBD               | TBD                  |

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

These pilot results motivate the full benchmark evaluation across all 10 items and all
four cases.

---

## How to Run

See the main evaluation README and `evaluation/evaluate.py` for full instructions.

Quick start:

```bash
cd ..
python evaluation/evaluate.py --model claude --items data/dataset.json --output results/
```
