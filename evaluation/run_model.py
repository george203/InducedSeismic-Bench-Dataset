"""
Query AI models with benchmark items and collect raw responses.

Supported model strings: claude, gpt4, gemini, llama
API keys read from environment: ANTHROPIC_API_KEY, OPENAI_API_KEY
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

import anthropic
import openai
from tqdm import tqdm

from judge_prompts import MODEL_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

# Default model IDs per model string
MODEL_IDS = {
    "claude": "claude-sonnet-4-6",
    "gpt4": "gpt-4.1",
    "gemini": "gemini-2.0-flash",
    "llama": "meta-llama/Llama-3.1-70B-Instruct",
}

MAX_TOKENS = 1024
RETRY_DELAY = 5  # seconds between retries
MAX_RETRIES = 3


def _build_prompt(item: dict) -> str:
    return MODEL_PROMPT_TEMPLATE.format(
        evidence_description=item["evidence_description"],
        question=item["question"],
    )


def _query_claude(prompt: str, model_id: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model=model_id,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _query_openai(prompt: str, model_id: str) -> str:
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=model_id,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def _query_with_retry(query_fn, *args, **kwargs) -> str:
    for attempt in range(MAX_RETRIES):
        try:
            return query_fn(*args, **kwargs)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning("API error (attempt %d/%d): %s — retrying in %ds",
                               attempt + 1, MAX_RETRIES, e, RETRY_DELAY)
                time.sleep(RETRY_DELAY)
            else:
                raise


def run_model(
    model: str,
    items: list[dict],
    output_path: Path | str | None = None,
) -> list[dict]:
    """
    Query a model with all benchmark items and return raw responses.

    Args:
        model:       Model string: "claude", "gpt4", "gemini", or "llama".
        items:       List of dataset items from dataset.json.
        output_path: If provided, save responses to this JSON file.

    Returns:
        List of response dicts: {item_id, model, model_id, prompt, response}.
    """
    if model not in MODEL_IDS:
        raise ValueError(f"Unknown model '{model}'. Choose from: {list(MODEL_IDS)}")

    model_id = MODEL_IDS[model]
    logger.info("Running %s (%s) on %d items", model, model_id, len(items))

    if model == "claude":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise EnvironmentError("ANTHROPIC_API_KEY not set")
        query_fn = lambda p: _query_with_retry(_query_claude, p, model_id)
    elif model in ("gpt4",):
        if not os.environ.get("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY not set")
        query_fn = lambda p: _query_with_retry(_query_openai, p, model_id)
    elif model == "gemini":
        # Gemini uses the OpenAI-compatible endpoint via OPENAI_API_KEY or GEMINI_API_KEY
        if not os.environ.get("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY (or Gemini-compatible key) not set")
        query_fn = lambda p: _query_with_retry(_query_openai, p, model_id)
    elif model == "llama":
        if not os.environ.get("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY (for OpenAI-compatible LLaMA endpoint) not set")
        query_fn = lambda p: _query_with_retry(_query_openai, p, model_id)
    else:
        raise ValueError(f"Model '{model}' not implemented")

    responses = []
    for item in tqdm(items, desc=f"Querying {model}"):
        prompt = _build_prompt(item)
        try:
            response_text = query_fn(prompt)
            status = "ok"
        except Exception as e:
            logger.error("Failed on item %s: %s", item["item_id"], e)
            response_text = f"ERROR: {e}"
            status = "error"

        responses.append({
            "item_id": item["item_id"],
            "case_id": item["case_id"],
            "tier": item["tier"],
            "model": model,
            "model_id": model_id,
            "prompt": prompt,
            "response": response_text,
            "status": status,
        })

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(responses, f, indent=2)
        logger.info("Responses saved to %s", out)

    return responses
