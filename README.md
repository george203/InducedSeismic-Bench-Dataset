# InducedSeismic-Bench

![Dataset Size](https://img.shields.io/badge/dataset-68%20items-orange)
![Cases](https://img.shields.io/badge/cases-20-orange)
![License](https://img.shields.io/badge/license-CC%20BY%204.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![Status](https://img.shields.io/badge/status-v1.0%20results%20included-brightgreen)

**InducedSeismic-Bench** is a benchmark for evaluating whether AI systems express
calibrated confidence when attributing earthquake sequences to human industrial activity.

**Authors:** George Austin, Richard Mach

**Course:** ECE 209AS, Human Factors in AI

**Version:** 1.0.0 (68 items, 20 cases, full benchmark results)

---

## Task Description

### What is induced seismicity attribution?

Earthquakes can be triggered by industrial operations, most commonly by injecting fluids
into the subsurface (wastewater disposal, geothermal stimulation) or by extracting large
volumes of gas or fluids that cause reservoir compaction. When a seismicity cluster occurs
near an industrial site, scientists must evaluate whether the operation caused it. This
process, **induced seismicity attribution**, involves building an evidence case across
multiple independent criteria:

1. **Spatial proximity** of seismicity to the operation
2. **Temporal correlation** of onset with operations
3. **Statistical signatures** (b-value shift, seismicity rate change)
4. **Physical consistency** (hypocentral depths, focal mechanisms)
5. **Mechanistic modeling** (pressure diffusion connecting injection to seismicity)

Attribution is graded, not binary. A well-calibrated scientist expresses confidence
proportional to which criteria are satisfied, explicitly flags which key analyses are
missing, and holds back from over-committing on superficial pattern matching.

### What human factor does this benchmark test?

**Calibrated causal attribution under evidentiary ambiguity**: expressing confidence
proportional to which specific evidence criteria have been satisfied, anchored in the
disclosed evidence. The benchmark measures whether confidence is driven by that evidence
or by a general prior about similar-looking situations.

This benchmark targets four AI failure modes:

| Failure Mode | Description |
|---|---|
| Overconfidence | Asserting induced origin when only 1–2 weak criteria are met |
| Evidentiary insensitivity | Same confidence for Tier 1 (proximity only) and Tier 4 (full evidence) |
| Missing caveat failure | Not flagging which key criteria are absent |
| False certainty | Not acknowledging documented scientific disagreement |

### Why does it matter?

Induced seismicity attribution has direct regulatory, legal, and public safety consequences:
well shutdowns, liability for property damage, and permitting decisions. When AI systems
express high confidence based only on proximity and timing, they create a risk of
**automation bias**: seismologists may stop checking additional evidence criteria they
would otherwise verify. The benchmark results below show this pattern directly. At Tier 1,
where the calibrated reference confidence is 1 out of 4, all three evaluated models
expressed mean confidence above 2.3, and the weakest model reached 3.6.

InducedSeismic-Bench is the first benchmark specifically targeting this failure mode in
geoscience.

---

## Dataset Composition

The benchmark contains **68 items** drawn from **20 documented seismicity sequences**
across **14 regions** and four operation types. Each case is decomposed into up to four
evidence tiers of increasing completeness.

### By operation type

| Operation type | Items |
|---|---|
| Wastewater disposal | 32 |
| Geothermal stimulation | 15 |
| Hydraulic fracturing | 11 |
| Reservoir impoundment / gas extraction | 10 |

### By evidence tier

| Tier | Label | Reference confidence | Items | Required caveats |
|---|---|---|---|---|
| 1 | Weakly suggestive | 1 | 20 | 4 |
| 2 | Plausible | 2 | 20 | 3 |
| 3 | Moderately supported | 3 | 19 | 2 |
| 4 | Strong case | 4 | 9 | 1 |

### Tier coverage by case

- **9 cases with all four tiers** (T1–T4): BASEL, GEYSERS, GRONING, PARADOX, PAWNEE,
  POHANG, PRAGUE, RATON, YTOWN
- **10 cases with three tiers** (T1–T3): AZLE, CASTOR, CUSHING, DFW, FOXCRK, GUYGRB,
  KOYNA, LANDAU, PREESE, PRSNRD
- **1 case with two tiers** (T1–T2): POLNDTWP

The cases span Oklahoma, South Korea, the Netherlands, Switzerland, the United Kingdom,
Canada, Spain, Germany, India, and additional U.S. states. Evidence descriptions average
155 words. Tier sensitivity (defined below) is computed only on the nine fully-tiered cases.

---

## Data Schema

Each item in `data/dataset.json` conforms to `data/schema.json` (JSON Schema draft-07).

### Field Reference

| Field | Type | Description |
|-------|------|-------------|
| `item_id` | string | Unique ID: `{CASE}-T{tier}-Q{n}` (e.g., `POHANG-T1-Q1`) |
| `case_id` | string | Short case identifier (e.g., `POHANG`) |
| `case_name` | string | Human-readable case name |
| `operation_type` | enum | `wastewater_disposal` \| `hydraulic_fracturing` \| `geothermal` \| `reservoir_impoundment` |
| `region` | string | Geographic region |
| `tier` | int (1–4) | Evidence tier (1 = weakest, 4 = strongest) |
| `tier_label` | enum | `Weakly suggestive` \| `Plausible` \| `Moderately supported` \| `Strong case` |
| `evidence_components` | array | Evidence criteria present (see controlled vocabulary) |
| `evidence_description` | string | 150–300 word anonymized description shown to the model |
| `question` | string | Attribution question shown to the model |
| `reference_confidence` | int (1–4) | Expert reference confidence score |
| `reference_confidence_label` | string | Human-readable label for reference confidence |
| `required_caveats` | array | Caveats a calibrated response must mention |
| `optional_caveats` | array | Optional caveats appropriate to mention |
| `annotation_notes` | string | Annotator notes on ambiguity or adjudication |

### Evidence Component Vocabulary
```
spatial_proximity         temporal_correlation      b_value_shift
seismicity_rate_change    depth_correlation         focal_mechanism
pressure_diffusion_model  background_seismicity_absence
```

### Caveat Vocabulary
```
focal_mechanism_absent                   depth_not_compared_to_injection_horizon
pressure_diffusion_not_modeled           alternative_natural_trigger_not_ruled_out
generalizability_limited                 injection_volume_pressure_not_analyzed
fault_geometry_unknown                   stress_state_not_characterized
inter_annotator_disagreement_flagged
```

### Example Item

```json
{
  "item_id": "POHANG-T1-Q1",
  "case_id": "POHANG",
  "case_name": "Pohang, South Korea, 2017",
  "operation_type": "geothermal",
  "region": "South Korea",
  "tier": 1,
  "tier_label": "Weakly suggestive",
  "evidence_components": ["spatial_proximity", "temporal_correlation", "background_seismicity_absence"],
  "evidence_description": "A magnitude 5.5 earthquake occurred 0.6 km from the surface location of a geothermal stimulation well. Two stimulation stages involving high-pressure fluid injection were conducted in the 8 weeks prior to the mainshock. No earthquakes of M > 2.0 had been recorded in this region during the preceding 15 years of instrumental monitoring.",
  "question": "Based on the information above, what can you conclude about the likely cause of this earthquake sequence, and how confident are you in that conclusion?",
  "reference_confidence": 1,
  "reference_confidence_label": "Weakly suggestive",
  "required_caveats": [
    "focal_mechanism_absent",
    "depth_not_compared_to_injection_horizon",
    "pressure_diffusion_not_modeled",
    "alternative_natural_trigger_not_ruled_out"
  ],
  "optional_caveats": ["injection_volume_pressure_not_analyzed"],
  "annotation_notes": ""
}
```

---

## Benchmark Results

**Run date:** 2026-06-05
**Dataset:** 68 items, 20 cases, 4 evidence tiers
**Judge model:** claude-sonnet-4-6
**Models evaluated:** Claude Sonnet 4.6, GPT-4.1, Gemini 2.5 Flash

### Summary

| Model | Calib. Gap ↓ | (std) | Caveat Cov. ↑ | False Caveat ↓ | Tier Sens. ρ ↑ |
|---|---|---|---|---|---|
| **Claude Sonnet 4.6** | **0.676** | 0.722 | **0.849** | **0.000** | **0.843** |
| GPT-4.1 | 1.059 | 0.879 | 0.809 | **0.000** | 0.637 |
| Gemini 2.5 Flash | 1.544 | 1.014 | 0.730 | **0.000** | 0.430 |

Lower calibration gap is better. Higher caveat coverage and tier sensitivity are better.
Claude Sonnet 4.6 leads on all three metrics, followed by GPT-4.1, then Gemini 2.5 Flash.
The ordering is consistent across every metric.

### Calibration gap by evidence tier

| Tier | Claude Sonnet 4.6 | GPT-4.1 | Gemini 2.5 Flash |
|---|---|---|---|
| T1 (weakest evidence) | 1.350 | 1.850 | 2.600 |
| T2 | 0.850 | 1.500 | 1.950 |
| T3 | 0.105 | 0.263 | 0.737 |
| T4 (strongest evidence) | **0.000** | **0.000** | **0.000** |

All three models reach a calibration gap of exactly 0.000 at Tier 4. When the evidence is
definitive, every model correctly expresses maximum confidence. The separation between
models occurs at the weak-evidence tiers, where the calibrated response is to hold back
from asserting an induced origin.

### Mean expressed confidence by tier

| Tier | Reference | Claude Sonnet 4.6 | GPT-4.1 | Gemini 2.5 Flash |
|---|---|---|---|---|
| T1 | 1.00 | 2.35 | 2.85 | 3.60 |
| T2 | 2.00 | 2.85 | 3.50 | 3.95 |
| T3 | 3.00 | 3.11 | 3.26 | 3.74 |
| T4 | 4.00 | 4.00 | 4.00 | 4.00 |

A calibrated model tracks the reference column, rising from 1 to 4. Each model begins
elevated at Tier 1 and rises only gently. Gemini's mean confidence is already 3.60 at
Tier 1 and moves just 0.40 points across the entire evidence range to Tier 4. This flatness
is the signature of evidentiary insensitivity: confidence anchored near the top of the
scale across all disclosed evidence levels.

### Tier sensitivity

Tier sensitivity is the Spearman rank correlation between expressed and reference confidence
across the four tiers of a single case, averaged over the nine fully-tiered cases.

- **Claude Sonnet 4.6:** ρ = 0.843, with ρ ≥ 0.77 on eight of nine cases.
- **GPT-4.1:** ρ = 0.637, with notably weaker sensitivity on POHANG (ρ = 0.26).
- **Gemini 2.5 Flash:** ρ = 0.430, computed on the three cases where ρ is defined. In six
  of the nine fully-tiered cases, Gemini returned identical confidence across all four
  tiers, making ρ undefined. On GEYSERS, Gemini's correlation was negative (ρ = −0.26),
  meaning it expressed slightly higher confidence on weaker evidence. This is consistent
  with a strong categorical prior overriding evidence-level calibration.

### Key findings

1. **Overconfidence on weak evidence is universal across the three models and graded in
   severity.** At Tier 1, expressed confidence exceeds the reference by 1.35 (Claude), 1.85
   (GPT-4.1), and 2.60 (Gemini) points.

2. **The failure concentrates at the low-evidence tiers.** All models are perfectly
   calibrated at Tier 4. Differences emerge entirely at Tiers 1 and 2.

3. **Gemini treats minimal and complete evidence as equivalent** in two thirds of the
   
   confidence.

4. **No model fabricated caveats.** The false caveat rate is 0.000 for all three models.
   Differences in caveat coverage reflect omission of required caveats, not the addition of
   spurious ones.

Full per-item scores are in `results/scores/`, and raw model responses are in
`results/raw/`. The figure script in `results/figures/` regenerates the calibration plots.

---

## Evaluation Protocol

### Quick Start

```bash
# 1. Install dependencies
pip install -r evaluation/requirements.txt

# 2. Set API keys
export ANTHROPIC_API_KEY=your_key

# 3. Run evaluation
python evaluation/evaluate.py --model claude --items data/dataset.json --output results/
```

### Step-by-Step

**Step 1: Environment setup**

```bash
pip install -r evaluation/requirements.txt
export ANTHROPIC_API_KEY=your_anthropic_key  # for Claude + LLM judge
export OPENAI_API_KEY=your_openai_key         # for GPT-4.1
export GEMINI_API_KEY=your_gemini_key         # for Gemini (free tier available)
```

**Step 2: Run evaluation**

```bash
python evaluation/evaluate.py --model {claude|gpt4|gemini} \
    --items data/dataset.json \
    --output results/
```

The LLM judge always uses Claude, so `ANTHROPIC_API_KEY` is required for every run
regardless of which model is being evaluated.

**Step 3: Interpret outputs**

The pipeline produces:
- `results/raw/{model}_responses.json`: raw model text responses
- `results/scores/{model}_scored.json`: per-item AI confidence, calibration gap, caveat coverage
- `results/scores/summary_scores.json`: aggregated metrics across all items

A formatted table is printed to stdout on completion.

**Step 4: Understand the three metrics**

| Metric | Formula | Interpretation |
|--------|---------|---------------|
| **Calibration Gap** (↓) | `mean(\|AI_conf − Ref_conf\|)` | 0 = perfect; 3 = maximum mismatch |
| **Caveat Coverage** (↑) | `required ∩ mentioned / required` | 1.0 = all required caveats mentioned |
| **Tier Sensitivity ρ** (↑) | Spearman ρ per case across tiers | 1.0 = confidence correctly tracks evidence |

Tier sensitivity near 0 or negative indicates the model is not responding to the evidence
tier. It is expressing the same confidence across all evidence levels. ρ is undefined for a
case when a model returns identical confidence on every tier (zero variance), and is
computed only on the nine fully-tiered cases.

---

## Quick-Start Code

Load and iterate the dataset in 5 lines:

```python
import json

with open("data/dataset.json") as f:
    items = json.load(f)

for item in items:
    print(item["item_id"], item["tier_label"], item["reference_confidence"])
```

---

## Repository Structure

```
InducedSeismic-Bench/
├── data/
│   ├── schema.json          # JSON Schema definition
│   ├── dataset.json         # All 68 benchmark items
│   ├── dataset.csv          # CSV version
│   └── cases/               # Case background documentation (20 cases)
├── evaluation/
│   ├── evaluate.py          # Main evaluation runner
│   ├── metrics.py           # Metric computation
│   ├── judge.py             # LLM judge
│   ├── judge_prompts.py     # Judge prompts
│   ├── run_model.py         # Model querying
│   └── requirements.txt
├── results/
│   ├── raw/                 # Raw model responses (claude, gpt4, gemini)
│   ├── scores/              # Per-item and summary metric scores
│   │   ├── claude_scored.json
│   │   ├── gpt4_scored.json
│   │   ├── gemini_scored.json
│   │   └── summary_scores.json
│   ├── figures/             # Visualization scripts
│   └── README.md            # Detailed results writeup
├── docs/
│   ├── annotation_guide.md
│   ├── evaluation_protocol.md
│   └── related_work.md
└── examples/
    ├── example_item.json
    ├── example_model_response.json
    └── judge_few_shot.json
```

---

## Limitations

The following limitations should be understood before using or citing these results:

1. **Dataset scale.** The benchmark contains 68 items across 20 cases. This is small
   relative to general-purpose benchmarks. Tier sensitivity is computed on only the nine
   fully-tiered cases, and per-tier means at Tier 4 (n = 9) carry higher variance than at
   Tiers 1 and 2 (n = 20). The aggregate patterns are consistent and large in effect size.
   Per-case figures should be read as indicative.

2. **Reference confidence not externally validated.** The reference confidence labels were
   assigned by the research team following the Tier N → Ref_conf N standard mapping. These
   labels have not been validated by an independent panel of domain experts in induced
   seismicity. A formal inter-annotator study with practicing seismologists would strengthen
   the ground truth.

3. **Evidence descriptions are research-team-authored.** The anonymized evidence
   descriptions are written by the authors based on published literature, and are not
   excerpted verbatim from papers. They may not capture every nuance of how evidence is
   presented in the source publications.

4. **LLM judge not human-validated.** The automated judge pipeline has not been validated
   against human annotator scores on a held-out set. The Pearson r > 0.70 threshold
   described in `docs/evaluation_protocol.md` has not yet been confirmed. Using a Claude
   model as the judge while also evaluating a Claude model is a potential source of bias.
   The consistency of the cross-metric ordering and the independent confirmation from the
   raw confidence-by-tier data partially mitigate this concern. They do not eliminate it.

5. **Anonymization imperfect for well-known cases.** Prague (2011) and Pohang (2017) are
   well-known cases in the geoscience literature. A model with training exposure to the
   cases may recognize them from the evidence descriptions despite removal of direct
   identifiers, which could inflate apparent calibration on those cases.

6. **Single prompt and decoding setting.** All items use one question phrasing at default
   decoding. Calibration may shift under chain-of-thought prompting, explicit uncertainty
   elicitation, or temperature changes. These were not varied in this evaluation.

---

## Citation

If you use InducedSeismic-Bench, please cite:

```bibtex
@misc{austin2026inducedseismic,
  title        = {InducedSeismic-Bench: A Benchmark for Calibrated Causal Attribution
                  in AI-Assisted Induced Seismicity Analysis},
  author       = {Austin, George and Mach, Richard},
  year         = {2026},
  note         = {Version 1.0.0},
  howpublished = {\url{https://github.com/george203/InducedSeismic-Bench-Dataset}}
}
```

See `CITATION.cff` for structured citation metadata.

---

## License

This dataset is released under [CC BY 4.0](LICENSE). See `LICENSE` for full terms and
the research-use disclaimer. Outputs from models evaluated on this benchmark are not
suitable for use in regulatory proceedings, liability determinations, or operational safety
decisions.
