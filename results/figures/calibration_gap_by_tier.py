#!/usr/bin/env python3
"""
Generate calibration gap by tier figure from summary_scores.json.

Usage:
    python calibration_gap_by_tier.py
    python calibration_gap_by_tier.py --scores ../../results/scores/summary_scores.json
    python calibration_gap_by_tier.py --output gap_by_tier.png
"""

import argparse
import json
from pathlib import Path


def plot_calibration_gap_by_tier(scores_path: str, output_path: str | None = None):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib and numpy are required: pip install matplotlib numpy")
        return

    with open(scores_path) as f:
        all_scores = json.load(f)

    # Filter to real model runs (skip _note, _schema, pilot entries)
    models = {
        k: v for k, v in all_scores.items()
        if not k.startswith("_") and isinstance(v, dict) and "calibration_gap" in v
    }

    if not models:
        print("No model results found in scores file. Run evaluate.py first.")
        return

    tiers = [1, 2, 3, 4]
    tier_labels = ["Tier 1\n(Weakly\nsuggestive)", "Tier 2\n(Plausible)",
                   "Tier 3\n(Moderately\nsupported)", "Tier 4\n(Strong case)"]
    x = np.arange(len(tiers))
    width = 0.8 / len(models)

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, (model_key, model_data) in enumerate(models.items()):
        by_tier = model_data["calibration_gap"]["by_tier"]
        gaps = [by_tier.get(str(t), by_tier.get(t, float("nan"))) for t in tiers]
        offset = (i - len(models) / 2 + 0.5) * width
        bars = ax.bar(x + offset, gaps, width, label=model_data.get("model", model_key), alpha=0.85)

    ax.set_xlabel("Evidence Tier", fontsize=12)
    ax.set_ylabel("Mean Calibration Gap (|AI − Reference|)", fontsize=12)
    ax.set_title("InducedSeismic-Bench: Calibration Gap by Evidence Tier", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(tier_labels, fontsize=10)
    ax.set_ylim(0, 3.5)
    ax.axhline(y=0, color="black", linewidth=0.8, linestyle="--", alpha=0.4)
    ax.legend(title="Model", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Figure saved to {output_path}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot calibration gap by tier")
    parser.add_argument(
        "--scores",
        default=str(Path(__file__).parents[1] / "scores" / "summary_scores.json"),
        help="Path to summary_scores.json",
    )
    parser.add_argument("--output", default=None, help="Output file path (PNG/PDF)")
    args = parser.parse_args()
    plot_calibration_gap_by_tier(args.scores, args.output)


if __name__ == "__main__":
    main()
