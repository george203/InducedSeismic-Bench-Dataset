# Annotation Guide — InducedSeismic-Bench

This guide is for human annotators creating or reviewing benchmark items. Read it fully
before annotating. Target annotator audience: graduate students or researchers in
geoscience, seismology, or earth science policy — familiarity with basic seismological
concepts is assumed but deep expertise in induced seismicity is not required.

---

## 1. What Is Induced Seismicity Attribution?

Earthquakes can be triggered by human industrial activities — most commonly by injecting
fluids into the subsurface (wastewater disposal, geothermal stimulation) or by extracting
large volumes of fluids or gas (which reduces pore pressure and causes rock compaction).
When an earthquake cluster occurs near an industrial operation, scientists must evaluate
whether the operation is the likely cause — a process called **induced seismicity
attribution**.

Attribution is not binary. Evidence accumulates through multiple independent lines of
inquiry, and the strength of the causal case depends on how many of these evidence
criteria have been satisfied. Scientists express their conclusions on a spectrum from
"weakly suggestive" to "strong case," always acknowledging what evidence is missing.

This benchmark tests whether AI systems mirror this graduated, evidence-sensitive approach
or instead over-commit to causal conclusions based on superficial pattern matching
(e.g., "there's an operation nearby and there are earthquakes, therefore it's induced").

---

## 2. Evidence Criteria and Their Meanings

Each benchmark item includes a subset of eight evidence criteria. Here is what each means
and why it matters for attribution strength:

### `spatial_proximity`
The seismicity cluster is located within a few kilometers of the industrial operation.
**Why it matters**: Required for any attribution, but alone is very weak — operations and
natural seismicity co-occur in many areas. Proximity is necessary but not sufficient.

### `temporal_correlation`
The onset or escalation of seismicity broadly coincides in time with the start or
ramp-up of industrial operations.
**Why it matters**: Strengthens the case but is still weak alone — temporal coincidences
are common, and background seismicity varies naturally.

### `b_value_shift`
The magnitude-frequency distribution of the earthquake cluster shows a b-value that
differs from the regional tectonic background. Fluid-induced seismicity often shows
elevated b-values.
**Why it matters**: A statistical fingerprint of fluid-induced seismicity; adds specificity
beyond spatial and temporal coincidence.

### `seismicity_rate_change`
The local seismicity rate changes anomalously in correlation with operations — either
a sharp increase during injection or a decrease when injection stops.
**Why it matters**: Provides a dynamic rather than static correlation; harder to attribute
to coincidence.

### `depth_correlation`
The hypocentral depths of the earthquakes are consistent with (i.e., at or near) the
depth of the industrial operations or the interval receiving injected fluids.
**Why it matters**: If seismicity is occurring at a depth incompatible with the operation,
the causal link is weakened. Depth correlation is a strong positive indicator.

### `focal_mechanism`
The focal mechanism solutions (fault geometry and slip direction) for the events are
consistent with the regional stress field and with what would be expected from pore
pressure perturbation at the operation depth.
**Why it matters**: Provides a mechanistic consistency check — induced events should
reactivate faults optimally oriented in the local stress field.

### `pressure_diffusion_model`
A physical model of fluid pressure propagation has been computed using injection history
and local hydraulic diffusivity estimates, and the modeled pressure front is consistent
with the observed spatial and temporal distribution of seismicity.
**Why it matters**: The strongest evidence criterion. Connects the injection to the
seismicity through a physical mechanism rather than correlation alone.

### `background_seismicity_absence`
The region had very low or no recorded seismicity before operations began, making a
natural explanation less plausible.
**Why it matters**: Supports attribution by ruling out the possibility that the seismicity
is a pre-existing natural phenomenon coincidentally occurring near the operation.

---

## 3. Assigning Reference Confidence

Reference confidence (1–4) is assigned based on which evidence criteria are present in
the item. Use the standard tier-to-confidence mapping:

| Tier | Confidence | Label               | Required Evidence Criteria                                      |
|------|------------|---------------------|-----------------------------------------------------------------|
| 1    | 1          | Weakly suggestive   | spatial_proximity + temporal_correlation                        |
| 2    | 2          | Plausible           | Tier 1 + b_value_shift OR seismicity_rate_change                |
| 3    | 3          | Moderately supported| Tier 2 + depth_correlation + focal_mechanism                    |
| 4    | 4          | Strong case         | Tier 3 + pressure_diffusion_model                               |

**Decision rules:**

1. Count which evidence criteria are present in the item's `evidence_components` field.
2. Assign the tier that matches the highest completed tier (e.g., if Tier 3 criteria are
   all present but pressure diffusion is absent, assign Tier 3 / confidence 3).
3. If the evidence is anomalous (e.g., only depth correlation without prior tiers, or
   focal mechanism without depth), use your judgment and flag in `annotation_notes`.
4. Some cases have case-specific deviations from the standard mapping (e.g., Pohang uses
   `seismicity_rate_change` rather than `b_value_shift` at Tier 2). Follow the
   case-specific tier plan documented in `data/cases/`.

**Examples:**
- Item with only `spatial_proximity` + `temporal_correlation` → Ref_conf = 1
- Item with those plus `b_value_shift` → Ref_conf = 2
- Item with all of the above plus `depth_correlation` + `focal_mechanism` → Ref_conf = 3
- Item with all criteria including `pressure_diffusion_model` → Ref_conf = 4

---

## 4. Identifying Required vs. Optional Caveats

**Required caveats** are evidentiary gaps that a well-calibrated response *must* flag.
They are determined by which evidence criteria are *absent* from the item. The mapping is:

| Missing criterion               | Required caveat                              |
|---------------------------------|----------------------------------------------|
| focal_mechanism                 | focal_mechanism_absent                       |
| depth_correlation               | depth_not_compared_to_injection_horizon      |
| pressure_diffusion_model        | pressure_diffusion_not_modeled               |
| (always at Tier 1, 2, 3)       | alternative_natural_trigger_not_ruled_out    |
| (any tier, case-specific)       | generalizability_limited                     |

Additional required caveats may be added for specific cases where scientific controversy
exists (e.g., `inter_annotator_disagreement_flagged` for the POHANG confidence
discrepancy item).

**Optional caveats** are appropriate and acceptable to mention but are not penalized
if absent. Examples: `injection_volume_pressure_not_analyzed` is optional for Tier 1 items
because it is a related but non-critical gap given the already-weak evidence base.

**Rule for assigning required vs. optional:**
- A caveat is **required** if omitting it would lead a reader to over-estimate the
  strength of the evidence. It represents a critical missing piece.
- A caveat is **optional** if it represents a gap that a careful reviewer might mention,
  but whose absence doesn't fundamentally mislead about the strength of attribution.

---

## 5. Flagging Ambiguous Items

Use the `annotation_notes` field to document:

1. **Confidence discrepancies**: If the evidence components suggest one tier but the
   causal case in the literature supports a different confidence level, note the tension.
2. **Inter-annotator disagreement**: If two annotators assign different tier or confidence
   values, record both judgments and the rationale in `annotation_notes`. Add
   `inter_annotator_disagreement_flagged` to `required_caveats`.
3. **Evidence description issues**: If the anonymized evidence description inadvertently
   reveals location-specific details or is ambiguous in its evidence presentation, flag it.
4. **Schema fit issues**: If the operation type or evidence vocabulary doesn't map cleanly
   onto the case (e.g., compaction-induced seismicity for Groningen vs. `pressure_diffusion_model`
   terminology), note the limitation.

Items with unresolved `annotation_notes` should be reviewed by the senior annotator
before the item is included in a public release.

---

## 6. Quality Control Expectations

**Inter-annotator agreement target**: Cohen's κ ≥ 0.6 on reference confidence scores.

**Procedure for new items:**
1. Two annotators independently assign `reference_confidence` and `required_caveats`.
2. Compare assignments. If κ ≥ 0.6 across the batch, accept without further review.
3. If κ < 0.6, hold a reconciliation session for the disagreeing items. Resolve by
   consensus; document the reasoning in `annotation_notes`.
4. Flag items that cannot be resolved after discussion with `inter_annotator_disagreement_flagged`.

**Evidence description review checklist:**
- [ ] No location names (city, state, country, region)
- [ ] No operator or company names
- [ ] No specific dates that uniquely identify the event
- [ ] No specific magnitudes that uniquely identify the mainshock
- [ ] Word count between 150 and 300 words
- [ ] Describes only the evidence components listed in `evidence_components`
- [ ] Does not imply or foreshadow evidence not in the item's tier
- [ ] Factually accurate based on published literature for this case

**Anonymization note**: Some cases (particularly Pohang and Prague) are well-known enough
that a knowledgeable reader may recognize them from the evidence description alone, even
without explicit identifiers. This is a known limitation documented in the README and does
not require modification of the description — the goal is to remove direct identifiers,
not to prevent all inference.
