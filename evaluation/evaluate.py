#!/usr/bin/env python3
"""
Main evaluation runner for InducedSeismic-Bench.

Usage:
    python evaluate.py --model claude --items data/dataset.json --output results/
    python evaluate.py --model gpt4 --items data/dataset.json --output results/
    python evaluate.py --judge-only --responses results/raw/claude_responses.json

Environment variables:
    ANTHROPIC_API_KEY  — required for --model claude (and for the LLM judge)
    OPENAI_API_KEY     — required for --model gpt4 / gemini / llama
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import anthropic
from tqdm import tqdm

# Allow running from the repo root or from the evaluation/ directory
sys.path.insert(0, str(Path(__file__).parent))

from judge import judge_response
from metrics import calibration_gap, caveat_coverage, tier_sensitivity
from run_model import run_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_items(items_path: str) -> list[dict]:
    with open(items_path) as f:
        return json.load(f)


def load_responses(responses_path: str) -> list[dict]:
    with open(responses_path) as f:
        return json.load(f)


def run_judge(
    responses: list[dict],
    items_by_id: dict[str, dict],
    client: anthropic.Anthropic,
) -> list[dict]:
    """Run the LLM judge on all responses and return scored records."""
    scored = []
    for resp in tqdm(responses, desc="Judging responses"):
        if resp.get("status") == "error":
            logger.warning("Skipping error response for %s", resp["item_id"])
            continue
        item = items_by_id.get(resp["item_id"])
        if item is None:
            logger.warning("No item found for response %s", resp["item_id"])
            continue
        try:
            result = judge_response(item, resp["response"], client=client)
            result["model"] = resp.get("model", "unknown")
            result["tier"] = item["tier"]
            result["case_id"] = item["case_id"]
            scored.append(result)
        except Exception as e:
            logger.error("Judge failed on %s: %s", resp["item_id"], e)
    return scored


def compute_and_print_metrics(scored: list[dict], model: str) -> dict:
    """Compute all three metrics and print a formatted summary."""
    ai_scores = [s["ai_confidence"] for s in scored]
    ref_scores = [s["ref_confidence"] for s in scored]
    tiers = [s["tier"] for s in scored]
    case_ids = [s["case_id"] for s in scored]

    required = [[]] * len(scored)  # already folded into coverage field
    mentioned = [s["caveat_present"] for s in scored]
    # Reconstruct required lists from scored records
    req_lists = [
        list(set(s["caveat_present"]) | set(s["caveat_absent"])) for s in scored
    ]

    gap_result = calibration_gap(ai_scores, ref_scores, tiers=tiers)
    cov_result = caveat_coverage(req_lists, mentioned, tiers=tiers)
    sens_result = tier_sensitivity(ai_scores, ref_scores, case_ids, tiers)

    summary = {
        "model": model,
        "n_items": len(scored),
        "calibration_gap": gap_result,
        "caveat_coverage": cov_result,
        "tier_sensitivity": sens_result,
    }

    # Print formatted table
    print(f"\n{'='*60}")
    print(f"  InducedSeismic-Bench Results — {model}")
    print(f"{'='*60}")
    print(f"  Items evaluated:        {len(scored)}")
    print(f"  Calibration Gap (↓):    {gap_result['mean_gap']:.3f}  (std={gap_result['std_gap']:.3f})")
    print(f"  Caveat Coverage  (↑):   {cov_result['mean_coverage']:.3f}")
    print(f"  False Caveat Rate (↓):  {cov_result['false_caveat_rate']:.3f}")
    print(f"  Tier Sensitivity ρ (↑): {sens_result['mean_rho']:.3f}")
    print()
    print("  By tier (calibration gap):")
    for t in (1, 2, 3, 4):
        v = gap_result["by_tier"][t]
        v_str = f"{v:.3f}" if v == v else "n/a"  # nan check
        print(f"    Tier {t}: {v_str}")
    print()
    print("  By case (tier sensitivity ρ):")
    for case, rho in sens_result["by_case"].items():
        rho_str = f"{rho:.3f}" if rho == rho else "n/a"
        print(f"    {case}: {rho_str}")
    print(f"{'='*60}\n")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Run InducedSeismic-Bench evaluation pipeline"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--model",
        choices=["claude", "gpt4", "gemini", "llama"],
        help="Model to evaluate (queries the model, then runs judge)",
    )
    group.add_argument(
        "--judge-only",
        action="store_true",
        help="Skip model querying; run judge on existing responses",
    )
    parser.add_argument(
        "--items",
        default="data/dataset.json",
        help="Path to dataset.json (default: data/dataset.json)",
    )
    parser.add_argument(
        "--output",
        default="results/",
        help="Output directory for raw responses and scores (default: results/)",
    )
    parser.add_argument(
        "--responses",
        help="Path to existing responses JSON (required with --judge-only)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    raw_dir = output_dir / "raw"
    scores_dir = output_dir / "scores"
    raw_dir.mkdir(parents=True, exist_ok=True)
    scores_dir.mkdir(parents=True, exist_ok=True)

    # Load dataset items
    logger.info("Loading items from %s", args.items)
    items = load_items(args.items)
    items_by_id = {item["item_id"]: item for item in items}

    if args.judge_only:
        if not args.responses:
            parser.error("--responses is required with --judge-only")
        logger.info("Loading responses from %s", args.responses)
        responses = load_responses(args.responses)
        model_name = responses[0].get("model", "unknown") if responses else "unknown"
    else:
        model_name = args.model
        raw_path = raw_dir / f"{model_name}_responses.json"
        logger.info("Querying %s...", model_name)
        responses = run_model(model_name, items, output_path=raw_path)
        logger.info("Responses saved to %s", raw_path)

    # Initialize judge client
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not set — required for LLM judge")
        sys.exit(1)
    judge_client = anthropic.Anthropic(api_key=api_key)

    # Run judge
    logger.info("Running LLM judge on %d responses...", len(responses))
    scored = run_judge(responses, items_by_id, judge_client)

    if not scored:
        logger.error("No scored items — check that responses and items match")
        sys.exit(1)

    # Compute metrics and print summary
    summary = compute_and_print_metrics(scored, model_name)

    # Save scores
    scores_path = scores_dir / "summary_scores.json"
    existing = {}
    if scores_path.exists():
        with open(scores_path) as f:
            existing = json.load(f)

    existing[model_name] = summary
    with open(scores_path, "w") as f:
        json.dump(existing, f, indent=2)
    logger.info("Scores saved to %s", scores_path)

    # Save per-item scored results
    scored_path = scores_dir / f"{model_name}_scored.json"
    with open(scored_path, "w") as f:
        json.dump(scored, f, indent=2)
    logger.info("Per-item scores saved to %s", scored_path)


if __name__ == "__main__":
    main()
