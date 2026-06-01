"""
LLM judge for extracting confidence scores and caveat coverage from model responses.
Uses claude-sonnet-4-6 (or GPT-4-class) as the judge model.
"""

from __future__ import annotations

import json
import logging
import os
import re

import anthropic

from judge_prompts import (
    CAVEAT_COVERAGE_SYSTEM,
    CAVEAT_COVERAGE_USER_TEMPLATE,
    CONFIDENCE_EXTRACTION_SYSTEM,
    CONFIDENCE_EXTRACTION_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)

JUDGE_MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 3


def _get_anthropic_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set")
    return anthropic.Anthropic(api_key=api_key)


def extract_confidence(response_text: str, client: anthropic.Anthropic | None = None) -> int:
    """
    Extract a 1–4 confidence score from a model response using an LLM judge.

    Args:
        response_text: The raw text response from the evaluated model.
        client:        Optional pre-initialized Anthropic client (created if None).

    Returns:
        Integer confidence score in [1, 4].

    Raises:
        ValueError: If the judge returns an unparseable or out-of-range score after retries.
    """
    if client is None:
        client = _get_anthropic_client()

    user_message = CONFIDENCE_EXTRACTION_USER_TEMPLATE.format(response=response_text)

    for attempt in range(MAX_RETRIES):
        try:
            message = client.messages.create(
                model=JUDGE_MODEL,
                max_tokens=16,
                system=CONFIDENCE_EXTRACTION_SYSTEM,
                messages=[{"role": "user", "content": user_message}],
            )
            raw = message.content[0].text.strip()
            # Extract the first digit found
            match = re.search(r"[1-4]", raw)
            if match:
                return int(match.group())
            logger.warning("Judge returned unparseable confidence on attempt %d: %r", attempt + 1, raw)
        except Exception as e:
            logger.warning("Judge API error on attempt %d: %s", attempt + 1, e)

    raise ValueError(f"Failed to extract confidence score after {MAX_RETRIES} attempts")


def extract_caveat_coverage(
    response_text: str,
    required_caveats: list[str],
    client: anthropic.Anthropic | None = None,
) -> dict[str, list[str]]:
    """
    Determine which required caveats are present in a model response.

    Args:
        response_text:     The raw text response from the evaluated model.
        required_caveats:  List of required caveat identifiers for this item.
        client:            Optional pre-initialized Anthropic client.

    Returns:
        {"present": [...], "absent": [...]} — lists of caveat identifiers.

    Raises:
        ValueError: If the judge returns invalid JSON after retries.
    """
    if client is None:
        client = _get_anthropic_client()

    user_message = CAVEAT_COVERAGE_USER_TEMPLATE.format(
        required_caveats=json.dumps(required_caveats),
        response=response_text,
    )

    for attempt in range(MAX_RETRIES):
        try:
            message = client.messages.create(
                model=JUDGE_MODEL,
                max_tokens=512,
                system=CAVEAT_COVERAGE_SYSTEM,
                messages=[{"role": "user", "content": user_message}],
            )
            raw = message.content[0].text.strip()
            # Strip markdown code fences if present
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            parsed = json.loads(raw)
            if "present" in parsed and "absent" in parsed:
                return parsed
            logger.warning("Judge returned unexpected JSON structure on attempt %d: %r", attempt + 1, raw)
        except json.JSONDecodeError:
            logger.warning("Judge returned invalid JSON on attempt %d: %r", attempt + 1, raw if "raw" in dir() else "")
        except Exception as e:
            logger.warning("Judge API error on attempt %d: %s", attempt + 1, e)

    raise ValueError(f"Failed to extract caveat coverage after {MAX_RETRIES} attempts")


def judge_response(
    item: dict,
    response_text: str,
    client: anthropic.Anthropic | None = None,
) -> dict:
    """
    Run both confidence extraction and caveat coverage on a single model response.

    Args:
        item:          Dataset item dict (must have 'required_caveats', 'reference_confidence').
        response_text: Raw model response text.
        client:        Optional pre-initialized Anthropic client.

    Returns:
        {
            "item_id":            str,
            "ai_confidence":      int,
            "ref_confidence":     int,
            "calibration_gap":    int,
            "caveat_present":     list[str],
            "caveat_absent":      list[str],
            "caveat_coverage":    float,
        }
    """
    if client is None:
        client = _get_anthropic_client()

    ai_conf = extract_confidence(response_text, client=client)
    caveat_result = extract_caveat_coverage(
        response_text, item["required_caveats"], client=client
    )

    ref_conf = item["reference_confidence"]
    required = item["required_caveats"]
    present = caveat_result.get("present", [])
    coverage = len(set(present) & set(required)) / len(required) if required else 1.0

    return {
        "item_id": item["item_id"],
        "ai_confidence": ai_conf,
        "ref_confidence": ref_conf,
        "calibration_gap": abs(ai_conf - ref_conf),
        "caveat_present": present,
        "caveat_absent": caveat_result.get("absent", []),
        "caveat_coverage": coverage,
    }
