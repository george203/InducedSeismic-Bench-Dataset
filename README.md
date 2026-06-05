# InducedSeismic-Bench

![Dataset Size](https://img.shields.io/badge/dataset-10%20items%20(draft)-orange)
![License](https://img.shields.io/badge/license-CC%20BY%204.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![Status](https://img.shields.io/badge/status-draft%20release-yellow)

**InducedSeismic-Bench** is a benchmark for evaluating whether AI systems express
calibrated confidence when attributing earthquake sequences to human industrial activity.

**Authors:** George Austin, Richard Mach
**Course:** ECE 209AS — Human Factors in AI
**Version:** 0.5.0 68 items

---

## Task Description

### What is induced seismicity attribution?

Earthquakes can be triggered by industrial operations — most commonly by injecting fluids
into the subsurface (wastewater disposal, geothermal stimulation) or by extracting large
volumes of gas or fluids (causing reservoir compaction). When a seismicity cluster occurs
near an industrial site, scientists must evaluate whether the operation caused it. This
process — **induced seismicity attribution** — involves building an evidence case across
multiple independent criteria:

1. **Spatial proximity** of seismicity to the operation
2. **Temporal correlation** of onset with operations
3. **Statistical signatures** (b-value shift, seismicity rate change)
4. **Physical consistency** (hypocentral depths, focal mechanisms)
5. **Mechanistic modeling** (pressure diffusion connecting injection to seismicity)

Attribution is not binary. A well-calibrated scientist expresses confidence proportional
to which criteria are satisfied, explicitly flags which key analyses are missing, and
avoids over-committing based on superficial pattern matching.

### What human factor does this benchmark test?

**Calibrated causal attribution under evidentiary ambiguity** — expressing confidence
proportional to which specific evidence criteria have been satisfied, not a general prior
about what caused similar-looking situations.

This benchmark targets four AI failure modes:

| Failure Mode | Description |
|---|---|
| Overconfidence | Asserting induced origin when only 1–2 weak criteria are met |
| Evidentiary insensitivity | Same confidence for Tier 1 (proximity only) and Tier 4 (full evidence) |
| Missing caveat failure | Not flagging which key criteria are absent |
| False certainty | Not acknowledging documented scientific disagreement |

### Why does it matter?

Induced seismicity attribution has direct regulatory, legal, and public safety consequences:
well shutdowns, liability for property damage, permitting decisions. When AI systems express
high confidence based only on proximity and timing, they risk causing **automation bias** —
seismologists may stop checking additional evidence criteria they would otherwise verify.
A well-documented case from 2018 illustrates this: two frontier AI models evaluated a
Tier 1 item (proximity and timing only) and expressed confidence scores of 3 and 4
(out of 4) respectively, when the reference confidence was 1. Neither mentioned any
of the four required caveats about missing evidence.

InducedSeismic-Bench is the first benchmark specifically targeting this failure mode in
geoscience.

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
| `optional_caveats` | array | Appropriate but not required caveats |
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
  "annotation_notes": "Note: reference_confidence discrepancy between slide deck (2) and dataset table (1). Tier 1 → 1 mapping used as canonical."
}
```

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
export OPENAI_API_KEY=your_openai_key         # for GPT-4 / Gemini / Llama
```

**Step 2: Run evaluation**

```bash
python evaluation/evaluate.py --model {claude|gpt4|gemini|llama} \
    --items data/dataset.json \
    --output results/
```

**Step 3: Interpret outputs**

The pipeline produces:
- `results/raw/{model}_responses.json` — raw model text responses
- `results/scores/{model}_scored.json` — per-item AI confidence, calibration gap, caveat coverage
- `results/scores/summary_scores.json` — aggregated metrics across all items

A formatted table is printed to stdout on completion.

**Step 4: Understand the three metrics**

| Metric | Formula | Interpretation |
|--------|---------|---------------|
| **Calibration Gap** (↓) | `mean(|AI_conf − Ref_conf|)` | 0 = perfect; 3 = maximum mismatch |
| **Caveat Coverage** (↑) | `required ∩ mentioned / required` | 1.0 = all required caveats mentioned |
| **Tier Sensitivity ρ** (↑) | Spearman ρ per case across tiers | 1.0 = confidence correctly tracks evidence |

Tier sensitivity near 0 or negative indicates the model is not responding to the evidence
tier at all — it is expressing the same confidence regardless of how much evidence is
provided.

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
│   ├── dataset.json         # All benchmark items
│   ├── dataset.csv          # CSV version
│   └── cases/               # Case background documentation
├── evaluation/
│   ├── evaluate.py          # Main evaluation runner
│   ├── metrics.py           # Metric computation
│   ├── judge.py             # LLM judge
│   ├── judge_prompts.py     # Judge prompts
│   ├── run_model.py         # Model querying
│   └── requirements.txt
├── results/
│   ├── raw/                 # Raw model responses
│   ├── scores/              # Computed metrics
│   └── figures/             # Visualization scripts
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

1. **Dataset size**: The current release contains 10 items (draft). The full target is
   250–300 items across additional cases and tiers. Metric estimates from 10 items have
   high variance and should be interpreted as preliminary.

2. **Case coverage**: All four cases are well-documented sequences from the published
   literature. Coverage is limited to cases with sufficient published evidence to construct
   tier-structured items. Edge cases, contested cases, and low-documentation sequences
   are not yet represented.

3. **Reference confidence not externally validated**: The reference confidence labels were
   assigned by the research team (George Austin, Richard Mach) following the Tier N →
   Ref_conf N standard mapping. These labels have not been validated by independent
   domain experts in induced seismicity.

4. **Evidence descriptions are research-team-authored**: The anonymized evidence descriptions
   are written by the authors based on published literature, not excerpted verbatim from
   papers. They may not perfectly capture the nuances of how evidence is actually presented
   in the source publications.

5. **LLM judge not yet human-validated**: The automated judge pipeline has not been
   validated against human annotator scores on a held-out set. The Pearson r > 0.70
   threshold described in `docs/evaluation_protocol.md` has not yet been confirmed.
   Results should be treated as preliminary pending this validation.

6. **Anonymization imperfect for well-known cases**: Prague (2011) and Pohang (2017) are
   well-known cases in the geoscience literature. A knowledgeable reader may identify the
   cases from the evidence descriptions despite removal of direct identifiers. This could
   allow models with training data exposure to the cases to respond from prior knowledge
   rather than from the provided evidence.

7. **Known confidence scale discrepancy**: The POHANG-T1-Q1 item has a documented
   discrepancy between source materials (slide deck labels Ref_conf = 2; dataset table
   labels Ref_conf = 1). The Tier 1 → Ref_conf = 1 mapping is used as canonical; this
   should be resolved through domain expert adjudication.

---

## Citation

If you use InducedSeismic-Bench, please cite:

```bibtex
@misc{austin2026inducedseismic,
  title        = {InducedSeismic-Bench: A Benchmark for Calibrated Causal Attribution
                  in AI-Assisted Induced Seismicity Analysis},
  author       = {Austin, George and Mach, Richard},
  year         = {2026},
  note         = {Version 0.1.0-draft},
  howpublished = {\url{https://github.com/george203/InducedSeismic-Bench}}
}
```

See `CITATION.cff` for structured citation metadata.

---

## License

This dataset is released under [CC BY 4.0](LICENSE). See `LICENSE` for full terms and
the research-use disclaimer.
