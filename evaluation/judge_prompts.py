CONFIDENCE_EXTRACTION_SYSTEM = """
You are an expert evaluator for an AI benchmark on induced seismicity attribution.
Your task is to extract the confidence level expressed in an AI model's response to an
attribution question. You must output a single integer from 1 to 4.

Scoring guide:
1 - The response uses language like: "cannot conclude", "insufficient evidence",
    "highly speculative", "no basis to determine", "highly uncertain"
2 - The response uses language like: "possibly", "may suggest", "preliminary indication",
    "weakly consistent", "cannot rule out a natural origin"
3 - The response uses language like: "likely", "points toward", "reasonably supported",
    "moderately confident", "plausible causal role"
4 - The response uses language like: "strongly indicates", "consistent with all criteria",
    "evidence supports", "high confidence", "clear induced case"

If the response contains mixed signals, choose the score that best represents the
dominant expressed confidence. Output ONLY a single integer (1, 2, 3, or 4). No explanation.
"""

CONFIDENCE_EXTRACTION_USER_TEMPLATE = """
Model response to evaluate:
{response}

What is the expressed confidence level (1-4)?
"""

CAVEAT_COVERAGE_SYSTEM = """
You are an expert evaluator for an AI benchmark on induced seismicity attribution.
You will be given a list of required caveats and an AI model's response.
Your task is to determine which required caveats are present in the response.

A caveat is considered "present" if the response clearly communicates the substance of
the caveat, even if it does not use the exact terminology. For example:
- "focal_mechanism_absent" is present if the response notes that fault geometry or
  focal mechanism data is not available or has not been analyzed.
- "depth_not_compared_to_injection_horizon" is present if the response notes that
  hypocentral depths have not been compared to the injection interval.
- "pressure_diffusion_not_modeled" is present if the response notes that pressure
  propagation or hydraulic diffusivity has not been modeled.
- "alternative_natural_trigger_not_ruled_out" is present if the response acknowledges
  that a natural tectonic origin cannot be excluded.
- "generalizability_limited" is present if the response notes that this evidence pattern
  may not apply to other cases or that additional cases would be needed to generalize.

Output a JSON object with two keys:
- "present": list of caveat identifiers that ARE present in the response
- "absent": list of caveat identifiers that are NOT present in the response

Use only identifiers from the provided required_caveats list.
"""

CAVEAT_COVERAGE_USER_TEMPLATE = """
Required caveats: {required_caveats}

Model response:
{response}

Which required caveats are present in the response?
Output valid JSON only, with keys "present" and "absent".
"""

MODEL_PROMPT_TEMPLATE = """You are being asked to evaluate evidence about an earthquake sequence.

{evidence_description}

{question}"""
