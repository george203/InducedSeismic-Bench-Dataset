# Related Work

This document positions InducedSeismic-Bench relative to prior benchmarks, datasets, and
evaluation frameworks in AI for science, epistemic calibration, and geoscience.

---

## AI Calibration and Epistemic Uncertainty Benchmarks

### General Calibration Benchmarks

**TruthfulQA** (Lin et al., 2022) evaluates whether language models produce truthful
answers on questions where humans commonly hold false beliefs. It is closest in spirit
to InducedSeismic-Bench in targeting overconfident or incorrect assertions, but operates
on factual knowledge retrieval rather than causal reasoning under evidentiary ambiguity.

**CalibratedQA** and related calibration datasets test whether model probability estimates
align with empirical accuracy rates. These operate at the token or logit level and do not
assess expressed natural-language confidence in domain-specific causal reasoning tasks.

**Measuring Calibration in Deep Learning** (Guo et al., 2017) established the
Expected Calibration Error (ECE) framework for evaluating probability calibration, which
is conceptually related to our Calibration Gap metric but operates at the level of
classifier probability outputs rather than expressed natural-language confidence.

### Science-Specific Benchmarks

**SciQ** (Welbl et al., 2017) and **ARC** (Clark et al., 2018) benchmark science question
answering, but focus on factual recall rather than causal attribution under incomplete
evidence.

**SciEval** (Sun et al., 2023) and **SciBench** (Wang et al., 2023) evaluate scientific
reasoning, including chemistry and physics problem-solving, but do not specifically target
confidence calibration or the expression of epistemic uncertainty proportional to evidence.

**MedQA** (Jin et al., 2021) and clinical reasoning benchmarks in medicine are the closest
analogs in high-stakes domains, as medical diagnosis shares the structure of causal
attribution under incomplete evidence with explicit uncertainty expression norms. However,
these operate in a domain with established clinical diagnostic standards rather than the
emerging attribution frameworks in geoscience.

---

## Human Factors and Automation Bias

### Automation Bias in AI Systems

**Parasuraman & Riley (1997)** defined automation bias as the tendency for humans to
over-rely on automated decision aids, particularly when the system expresses high
confidence. The induced seismicity context is a high-stakes application where automation
bias from overconfident AI is a documented concern in the science policy literature.

**Cummings (2004)** studied automation bias in military decision-making contexts, finding
that humans frequently fail to question automated recommendations even when evidence
should prompt skepticism. InducedSeismic-Bench operationalizes this concern: if AI systems
express high confidence on weak evidence, domain scientists using AI assistance may forgo
verification steps they would otherwise perform.

**Goddard et al. (2012)** reviewed automation bias in medical diagnosis, documenting
how high-confidence AI outputs lead clinicians to over-rely on potentially incorrect
recommendations. The regulatory consequences of induced seismicity attribution errors
(well shutdowns, liability determinations) create analogous risks.

---

## Induced Seismicity Literature

### Attribution Frameworks

**Induced Seismicity Score (ISS)** proposed by Villaseñor et al. (2020) and related
attribution scoring systems in the geoscience literature provide a formal framework for
grading the strength of induced seismicity evidence. InducedSeismic-Bench's tier system
(Tiers 1–4) is directly inspired by these frameworks, operationalizing them as benchmark
items with controlled evidence subsets.

**Ellsworth (2013)** in *Science* provided a widely-cited review of injection-induced
earthquakes, establishing the key evidence criteria that constitute the geoscience
community's standard for attribution. The eight evidence components in InducedSeismic-Bench
draw from this and subsequent literature.

**Foulger et al. (2018)** "Global review of human-induced earthquakes" provides the most
comprehensive catalog of documented induced seismicity cases, forming the pool from
which InducedSeismic-Bench cases are drawn.

### Case-Specific Literature

See `data/cases/` for per-case source publications. Key references:
- Prague, OK: Keranen et al. (2013), Sumy et al. (2014)
- Pohang, SK: Kim et al. (2018), Grigoli et al. (2018), Woo et al. (2019)
- Raton Basin, CO: Rubinstein et al. (2014)
- Groningen, NL: van Thienen-Visser & Breunese (2015), Bourne et al. (2014)

---

## Positioning of InducedSeismic-Bench

InducedSeismic-Bench occupies a distinct niche at the intersection of several research
threads:

1. **It is the first benchmark specifically targeting calibrated causal attribution in
   geoscience.** Prior science benchmarks focus on factual recall or mathematical
   reasoning, not the graduated expression of confidence proportional to evidence.

2. **It operationalizes a real human factors risk.** Unlike abstract calibration benchmarks,
   InducedSeismic-Bench is motivated by a documented automation bias concern in a domain
   with legal and regulatory consequences (Foulger et al., 2018; Ellsworth, 2013).

3. **It uses a controlled evidence manipulation design.** By varying which evidence
   components are included while holding the case context constant, InducedSeismic-Bench
   can isolate whether AI confidence is driven by the evidence or by a prior — a design
   not found in prior science QA benchmarks.

4. **It measures a distinct failure mode: evidentiary insensitivity.** The tier sensitivity
   metric (Spearman ρ) captures whether AI confidence tracks evidence accumulation, a
   failure mode not captured by accuracy or ECE metrics in prior calibration work.

**Limitations relative to prior work**: The current dataset (10 items, 4 cases) is small
compared to established benchmarks (TruthfulQA: 817 items; ARC: 7,787 items). The 250–300
item target for the full dataset will partially address this limitation, but the specialized
domain will inherently constrain dataset scale relative to general-purpose benchmarks.

---

## References

- Clark, P., et al. (2018). Think you have solved question answering? Try ARC. *arXiv:1803.05457*.
- Cummings, M. L. (2004). Automation bias in intelligent time critical decision support systems. *AIAA 3rd Intelligent Systems Conference*.
- Ellsworth, W. L. (2013). Injection-induced earthquakes. *Science*, 341(6142).
- Foulger, G. R., et al. (2018). Global review of human-induced earthquakes. *Earth-Science Reviews*, 178, 438–514.
- Goddard, K., et al. (2012). Automation bias: A systematic review of frequency, effect mediators, and mitigators. *Journal of the American Medical Informatics Association*, 19(1), 121–127.
- Guo, C., et al. (2017). On calibration of modern neural networks. *ICML 2017*.
- Jin, D., et al. (2021). What disease does this patient have? A large-scale open domain question answering dataset from medical exams. *Applied Sciences*, 11(14).
- Lin, S., et al. (2022). TruthfulQA: Measuring how models mimic human falsehoods. *ACL 2022*.
- Parasuraman, R., & Riley, V. (1997). Humans and automation: Use, misuse, disuse, abuse. *Human Factors*, 39(2), 230–253.
- Sun, L., et al. (2023). SciEval: A multi-level large language model evaluation benchmark for scientific research. *AAAI 2024*.
- Wang, X., et al. (2023). SciBench: Evaluating college-level scientific problem-solving abilities of large language models. *arXiv:2307.10635*.
- Welbl, J., et al. (2017). Crowdsourcing multiple choice science questions. *EMNLP 2017 Workshop*.
