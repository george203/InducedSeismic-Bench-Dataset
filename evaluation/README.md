# Evaluation

This directory contains the evaluation pipeline for InducedSeismic-Bench.

## Files

| File | Description |
|------|-------------|
| `evaluate.py` | Main evaluation runner — orchestrates model querying and scoring |
| `run_model.py` | Query AI models and collect raw responses |
| `judge.py` | LLM judge for extracting confidence scores and caveat coverage |
| `judge_prompts.py` | System and user prompt templates for the LLM judge |
| `metrics.py` | Pure Python metric computation (calibration gap, caveat coverage, tier sensitivity) |
| `requirements.txt` | Python dependency list |

## Setup

```bash
pip install -r evaluation/requirements.txt
```

Set API keys in your environment:

```bash
export ANTHROPIC_API_KEY=your_key_here   # required for Claude + LLM judge
export OPENAI_API_KEY=your_key_here      # required for GPT-4 / Gemini / Llama
```

Or use a `.env` file in the repo root (loaded by `python-dotenv`).

## Running Evaluation

### Evaluate a model end-to-end

```bash
python evaluation/evaluate.py --model claude --items data/dataset.json --output results/
python evaluation/evaluate.py --model gpt4  --items data/dataset.json --output results/
```

Supported `--model` values: `claude`, `gpt4`, `gemini`, `llama`

This will:
1. Query the model on all 10 items
2. Save raw responses to `results/raw/{model}_responses.json`
3. Run the LLM judge on each response
4. Compute the three metrics
5. Save scores to `results/scores/summary_scores.json`
6. Print a formatted summary table

### Run judge on existing responses

```bash
python evaluation/evaluate.py --judge-only \
    --responses results/raw/claude_responses.json \
    --items data/dataset.json \
    --output results/
```

## Output Files

After a full evaluation run:

```
results/
├── raw/
│   └── claude_responses.json      # Raw model outputs per item
└── scores/
    ├── summary_scores.json        # Aggregated metrics per model
    └── claude_scored.json         # Per-item judge scores
```

## Metrics Summary

| Metric | Formula | Direction |
|--------|---------|-----------|
| Calibration Gap | `mean(|AI_conf − Ref_conf|)` | Lower is better |
| Caveat Coverage | `|required ∩ mentioned| / |required|` | Higher is better |
| Tier Sensitivity ρ | Spearman ρ(AI_conf, Ref_conf) per case | Higher is better |

See `docs/evaluation_protocol.md` for full metric definitions and interpretation guidance.

## Using metrics.py Directly

The metric functions are pure Python with no I/O dependencies:

```python
from evaluation.metrics import calibration_gap, caveat_coverage, tier_sensitivity

# Example: compute calibration gap
ai_scores  = [3, 2, 3, 4, 1, 2, 3, 1, 2, 1]
ref_scores = [1, 2, 3, 4, 1, 2, 3, 1, 2, 1]
tiers      = [1, 2, 3, 4, 1, 2, 3, 1, 2, 1]

result = calibration_gap(ai_scores, ref_scores, tiers=tiers)
print(result["mean_gap"])       # float
print(result["by_tier"])        # {1: float, 2: float, 3: float, 4: float}
```
