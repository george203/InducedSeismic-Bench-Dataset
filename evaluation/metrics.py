"""
Metric computation for InducedSeismic-Bench.

Three metrics:
  1. calibration_gap   — mean absolute difference between AI and reference confidence
  2. caveat_coverage   — recall over required caveats + false caveat rate
  3. tier_sensitivity  — Spearman ρ between AI and reference confidence, grouped by case
"""

from __future__ import annotations

import numpy as np
from scipy import stats
from collections import defaultdict


def calibration_gap(
    ai_scores: list[int],
    ref_scores: list[int],
    tiers: list[int] | None = None,
) -> dict:
    """
    Compute mean absolute calibration gap between AI and reference confidence scores.

    Args:
        ai_scores:  AI-expressed confidence scores extracted by the judge (1–4 each).
        ref_scores: Reference confidence scores from the dataset (1–4 each).
        tiers:      Optional tier label for each item (1–4). When provided, also
                    computes per-tier breakdown.

    Returns:
        {
            "mean_gap": float,
            "std_gap":  float,
            "by_tier":  {1: float, 2: float, 3: float, 4: float},
            "n_items":  int,
        }
        by_tier values are NaN for tiers with no items.
    """
    if len(ai_scores) != len(ref_scores):
        raise ValueError("ai_scores and ref_scores must have the same length")
    if not ai_scores:
        raise ValueError("Score lists must not be empty")

    gaps = [abs(a - r) for a, r in zip(ai_scores, ref_scores)]
    result: dict = {
        "mean_gap": float(np.mean(gaps)),
        "std_gap": float(np.std(gaps, ddof=1) if len(gaps) > 1 else 0.0),
        "n_items": len(gaps),
    }

    by_tier: dict[int, float] = {}
    if tiers is not None:
        if len(tiers) != len(ai_scores):
            raise ValueError("tiers must have the same length as score lists")
        for t in (1, 2, 3, 4):
            tier_gaps = [g for g, tier in zip(gaps, tiers) if tier == t]
            by_tier[t] = float(np.mean(tier_gaps)) if tier_gaps else float("nan")
    else:
        by_tier = {t: float("nan") for t in (1, 2, 3, 4)}

    result["by_tier"] = by_tier
    return result


def caveat_coverage(
    required_caveats: list[list[str]],
    mentioned_caveats: list[list[str]],
    optional_caveats: list[list[str]] | None = None,
    tiers: list[int] | None = None,
) -> dict:
    """
    Compute caveat recall over required caveats and false-caveat rate.

    A "false caveat" is any caveat the model mentions that is neither in required_caveats
    nor in optional_caveats for that item — i.e., an invented or inapplicable caveat.

    Args:
        required_caveats:  For each item, the list of required caveat identifiers.
        mentioned_caveats: For each item, the list of caveats the judge found present.
        optional_caveats:  For each item, the list of optional (acceptable) caveats.
                           If None, false caveat rate is computed against required only.
        tiers:             Optional tier label for each item (1–4).

    Returns:
        {
            "mean_coverage":    float,   # mean per-item recall over required set
            "false_caveat_rate": float,  # mean per-item fraction of mentioned caveats
                                          # that are neither required nor optional
            "by_tier":          {1: float, 2: float, 3: float, 4: float},
            "n_items":          int,
        }
    """
    n = len(required_caveats)
    if len(mentioned_caveats) != n:
        raise ValueError("required_caveats and mentioned_caveats must have the same length")
    if optional_caveats is not None and len(optional_caveats) != n:
        raise ValueError("optional_caveats must have the same length as other inputs")
    if not required_caveats:
        raise ValueError("Input lists must not be empty")

    per_item_coverage: list[float] = []
    per_item_false_rate: list[float] = []

    for i in range(n):
        req = set(required_caveats[i])
        mentioned = set(mentioned_caveats[i])
        opt = set(optional_caveats[i]) if optional_caveats else set()

        # Recall: fraction of required caveats that were mentioned
        coverage = len(req & mentioned) / len(req) if req else 1.0
        per_item_coverage.append(coverage)

        # False caveat rate: fraction of mentioned caveats not in required OR optional
        allowed = req | opt
        false_caveats = mentioned - allowed
        false_rate = len(false_caveats) / len(mentioned) if mentioned else 0.0
        per_item_false_rate.append(false_rate)

    result: dict = {
        "mean_coverage": float(np.mean(per_item_coverage)),
        "false_caveat_rate": float(np.mean(per_item_false_rate)),
        "n_items": n,
    }

    by_tier: dict[int, float] = {}
    if tiers is not None:
        if len(tiers) != n:
            raise ValueError("tiers must have the same length as other inputs")
        for t in (1, 2, 3, 4):
            tier_cov = [c for c, tier in zip(per_item_coverage, tiers) if tier == t]
            by_tier[t] = float(np.mean(tier_cov)) if tier_cov else float("nan")
    else:
        by_tier = {t: float("nan") for t in (1, 2, 3, 4)}

    result["by_tier"] = by_tier
    return result


def tier_sensitivity(
    ai_scores: list[int],
    ref_scores: list[int],
    case_ids: list[str],
    tiers: list[int],
) -> dict:
    """
    Compute Spearman ρ between AI confidence and reference confidence, grouped by case.

    For each case with at least 2 items across different tiers, compute the Spearman
    rank correlation between the AI-expressed confidence and the reference confidence.
    A ρ near 1.0 means the model correctly tracks evidence accumulation; ρ near 0.0
    means the model ignores the tier structure.

    Args:
        ai_scores:  AI-expressed confidence scores (1–4 each).
        ref_scores: Reference confidence scores (1–4 each).
        case_ids:   Case identifier for each item (e.g. "PRAGUE", "POHANG").
        tiers:      Evidence tier for each item (1–4).

    Returns:
        {
            "mean_rho": float,           # mean ρ across cases with >= 2 items
            "by_case":  {str: float},    # per-case Spearman ρ
            "n_cases":  int,
        }
        Cases with fewer than 2 items are excluded from mean_rho but included in by_case
        as NaN.
    """
    if not (len(ai_scores) == len(ref_scores) == len(case_ids) == len(tiers)):
        raise ValueError("All input lists must have the same length")
    if not ai_scores:
        raise ValueError("Input lists must not be empty")

    case_data: dict[str, list] = defaultdict(list)
    for ai, ref, case, tier in zip(ai_scores, ref_scores, case_ids, tiers):
        case_data[case].append((tier, ai, ref))

    by_case: dict[str, float] = {}
    rho_values: list[float] = []

    for case, records in case_data.items():
        records_sorted = sorted(records, key=lambda x: x[0])
        ai_case = [r[1] for r in records_sorted]
        ref_case = [r[2] for r in records_sorted]

        if len(ai_case) < 2:
            by_case[case] = float("nan")
            continue

        # Check for zero variance (constant scores → ρ undefined)
        if len(set(ai_case)) == 1 or len(set(ref_case)) == 1:
            by_case[case] = float("nan")
            continue

        rho, _ = stats.spearmanr(ai_case, ref_case)
        by_case[case] = float(rho)
        rho_values.append(float(rho))

    mean_rho = float(np.mean(rho_values)) if rho_values else float("nan")

    return {
        "mean_rho": mean_rho,
        "by_case": by_case,
        "n_cases": len([v for v in by_case.values() if not np.isnan(v)]),
    }
