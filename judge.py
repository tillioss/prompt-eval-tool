"""
LLM-as-a-Judge evaluation logic using Gemini API
"""
import re
import google.generativeai as genai
from typing import Tuple, Optional, Dict, List, Any
import json


EVALUATION_PROMPT = """You are an expert evaluator assessing the quality of AI-generated answers.

**Context/Question:**
---
{question}
---

**Answer:**
---
{answer}
---

Please evaluate the answer based on the following criteria on a scale of 1 to 10:

1.  **Relevance**: How relevant is the response to the given input and context?
    - 1: Completely irrelevant.
    - 5: Partially relevant, but misses key aspects of the question.
    - 10: Perfectly relevant and directly addresses all parts of the question.

2.  **Clarity**: How clear and understandable is the generated output?
    - 1: Incoherent and impossible to understand.
    - 5: Understandable, but requires effort to follow due to poor structure or jargon.
    - 10: Perfectly clear, concise, and easy to understand.
    
3.  **Consistency**: How consistent are the results across multiple runs?
    - 1: Highly inconsistent and contradictory.
    - 5: Generally consistent, but with some contradictions.
    - 10: Perfectly consistent and reliable.
    
4.  **Creativity/Innovation**: For creative tasks, how original or innovative is the output?
    - 1: Plagiarized or completely unoriginal.
    - 5: Some originality, but mostly derivative.
    - 10: Highly original and innovative.

Provide your evaluation in the following format:

**Relevance:** [Your detailed feedback on relevance]
**Relevance Score:** [A number from 1 to 10]

**Clarity:** [Your detailed feedback on clarity]
**Clarity Score:** [A number from 1 to 10]

**Consistency:** [Your detailed feedback on consistency]
**Consistency Score:** [A number from 1 to 10]

**Creativity/Innovation:** [Your detailed feedback on creativity]
**Creativity Score:** [A number from 1 to 10]

**Total Score:** [The average of all scores, from 1 to 10]
"""


EVALUATION_PROMPT_INDIVIDUAL = """You are an expert evaluator assessing the quality of AI-generated answers.

**Context/Question:**
---
{question}
---

**Answer:**
---
{answer}
---

Please evaluate the answer based on the following criteria on a scale of 1 to 10:

1.  **Relevance**: How relevant is the response to the given input and context?
    - 1: Completely irrelevant.
    - 5: Partially relevant, but misses key aspects of the question.
    - 10: Perfectly relevant and directly addresses all parts of the question.

2.  **Clarity**: How clear and understandable is the generated output?
    - 1: Incoherent and impossible to understand.
    - 5: Understandable, but requires effort to follow due to poor structure or jargon.
    - 10: Perfectly clear, concise, and easy to understand.

Provide your evaluation in the following format:

**Relevance:** [Your detailed feedback on relevance]
**Relevance Score:** [A number from 1 to 10]

**Clarity:** [Your detailed feedback on clarity]
**Clarity Score:** [A number from 1 to 10]
"""


# Template guide for batch-level evaluation (Consistency & Creativity only)
EVALUATION_PROMPT_BATCH_GUIDE = """You are an expert evaluator. Evaluate the ENTIRE batch only for Consistency and Creativity.

Definitions (batch-level):
- Consistency (1–10): How consistent are the results across multiple runs? Coherence across answers, no contradictions, stable tone/format.
- Creativity (1–10): For creative tasks, how original or innovative is the output? Originality/diversity across answers, avoids generic templates.

Provide output in exactly this format:
Batch Evaluation
Consistency: <brief rationale>
Consistency Score: <integer 1-10>
Creativity: <brief rationale>
Creativity Score: <integer 1-10>
"""


def configure_gemini(api_key: str) -> None:
    """Configure the Gemini API with the provided API key."""
    genai.configure(api_key=api_key)


def flatten_json_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Inline $defs references into a self-contained schema (remove $defs).

    This converts Pydantic's JSON Schema with $defs/$ref into a flat schema that
    Gemini Structured Output accepts.
    """
    if not isinstance(schema, dict):
        return schema

    defs: Dict[str, Any] = schema.get("$defs") or schema.get("definitions") or {}

    unsupported_keys = {"$defs", "definitions", "$schema", "$id", "title", "description", "examples",
                        "maxItems", "minItems", "uniqueItems", "maxLength", "minLength", "pattern", "format",
                        "maximum", "minimum", "exclusiveMaximum", "exclusiveMinimum", "multipleOf", "default",
                        "nullable", "const", "oneOf", "anyOf", "allOf", "not", "deprecated", "readOnly",
                        "writeOnly", "contentMediaType", "contentEncoding"}
    allowed_keys = {"type", "properties", "required", "items", "additionalProperties", "enum"}

    def resolve(node: Any) -> Any:
        if isinstance(node, dict):
            # Replace $ref with the referenced definition
            if "$ref" in node and isinstance(node["$ref"], str):
                ref: str = node["$ref"]
                if ref.startswith("#/$defs/"):
                    key = ref.split("/")[-1]
                    target = defs.get(key)
                    if isinstance(target, dict):
                        return resolve(target.copy())
                elif ref.startswith("#/definitions/"):
                    key = ref.split("/")[-1]
                    target = defs.get(key)
                    if isinstance(target, dict):
                        return resolve(target.copy())
                # If unknown $ref, drop it to avoid invalid field
                node = {k: v for k, v in node.items() if k != "$ref"}
            # Recurse into dict
            filtered = {k: v for k, v in node.items() if k in allowed_keys or k not in unsupported_keys}
            # If 'items' is a dict, resolve it; if it's a list, take the first schema
            if "items" in filtered:
                if isinstance(filtered["items"], list) and filtered["items"]:
                    filtered["items"] = resolve(filtered["items"][0])
            return {k: resolve(v) for k, v in filtered.items() if k in allowed_keys}
        if isinstance(node, list):
            return [resolve(item) for item in node]
        return node

    flat = resolve(schema)

    def clean(node: Any) -> Any:
        if isinstance(node, dict):
            # Normalize object schemas
            if node.get("type") == "object":
                props = node.get("properties")
                if not isinstance(props, dict):
                    props = {}
                # Recursively clean each property schema
                props = {k: clean(v) for k, v in props.items()}

                # Filter required to only existing properties
                req = node.get("required")
                if isinstance(req, list):
                    req = [r for r in req if isinstance(r, str) and r in props]
                    if req:
                        node["required"] = req
                    else:
                        node.pop("required", None)

                # Ensure properties non-empty for Gemini OBJECT type
                if not props:
                    # Provide a minimal permissive property
                    props = {"_": {"type": "string"}}
                node["properties"] = props

            # Normalize array schemas
            if node.get("type") == "array":
                items = node.get("items")
                if not isinstance(items, dict):
                    node["items"] = {"type": "string"}

            # Remove any lingering unsupported keys
            for k in list(node.keys()):
                if k in unsupported_keys and k not in {"properties", "items"}:
                    node.pop(k, None)

            # Recurse for nested dicts
            return {k: clean(v) for k, v in node.items()}
        if isinstance(node, list):
            return [clean(x) for x in node]
        return node

    if isinstance(flat, dict):
        for k in list(unsupported_keys):
            flat.pop(k, None)
        flat = clean(flat)
    return flat


def _extract_json_object(text: str) -> Optional[str]:
    """Extract the first top-level JSON object from a text blob.

    Handles code fences and surrounding prose. Returns the JSON string if found.
    """
    if not text:
        return None
    # Strip common markdown fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        # remove opening fence and optional language tag
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
    # Find first '{' and matching '}' by counting braces
    start = cleaned.find('{')
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(cleaned)):
        ch = cleaned[i]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                candidate = cleaned[start:i+1]
                # Validate it's JSON
                try:
                    json.loads(candidate)
                    return candidate
                except Exception:
                    return None
    return None


def evaluate_with_gemini(
    question: str,
    answer: str,
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.5,
    mode: str = "individual"
) -> Tuple[str, Dict[str, Optional[int]], str]:
    """
    Evaluate an answer using Gemini API.
    
    Args:
        question: The original question
        answer: The model-generated answer to evaluate
        model_name: The Gemini model to use for evaluation
        temperature: The temperature for the model generation
    
    Returns:
        Tuple of (feedback_text, scores_dict, prompt_text)
    """
    try:
        # Create the prompt
        if mode == "individual":
            prompt = EVALUATION_PROMPT_INDIVIDUAL.format(question=question, answer=answer)
        else:
            prompt = EVALUATION_PROMPT.format(question=question, answer=answer)
        
        # Initialize the model
        generation_config = {"temperature": temperature}
        model = genai.GenerativeModel(
            model_name,
            generation_config=generation_config
        )
        
        # Generate evaluation
        response = model.generate_content(prompt)
        
        # Extract the response text
        feedback_text = response.text
        
        # Parse the rating from the response
        scores = {
            "total": extract_rating(feedback_text),
            "relevance": extract_relevance_score(feedback_text),
            "clarity": extract_clarity_score(feedback_text),
            "consistency": extract_consistency_score(feedback_text),
            "creativity": extract_creativity_score(feedback_text),
        }
            
        return feedback_text, scores, prompt
        
    except Exception as e:
        error_msg = f"Error during evaluation: {str(e)}"
        prompt_for_error = (
            EVALUATION_PROMPT_INDIVIDUAL if mode == "individual" else EVALUATION_PROMPT
        ).format(question=question, answer=answer)
        return error_msg, {
            "total": None, "relevance": None, "clarity": None,
            "consistency": None, "creativity": None
        }, prompt_for_error


def _build_batch_prompt(pairs: List[Tuple[str, str]]) -> str:
    count = len(pairs)
    header = (
        "You are an expert evaluator. Evaluate the ENTIRE batch of input→answer pairs only for: (1) Consistency across answers and (2) Creativity/Originality across the set.\n\n"
        "Definitions (batch-level):\n"
        "- Consistency (1–10): How consistent are the results across multiple runs? Similar prompts produce coherent, non-contradictory, and stylistically aligned answers. Higher = fewer contradictions, stable reasoning, uniform formatting/terminology when appropriate.\n"
        "- Creativity (1–10): For creative tasks, how original or innovative is the output? Answers demonstrate originality and non-trivial insight without being generic or templated. Higher = novel, diverse, and contextually appropriate variations.\n\n"
        f"Data ({count} pairs):\n"
    )
    body_lines = []
    for idx, (inp, ans) in enumerate(pairs, start=1):
        body_lines.append(f"Pair {idx}:\nInput:\n{inp}\nAnswer:\n{ans}\n")
    footer = (
        "Instructions:\n"
        "- Judge at the batch level only. Do NOT provide per-item relevance/clarity.\n"
        "- Consider conflicts/contradictions, tone/format drift, and reasoning stability for Consistency.\n"
        "- Consider originality, diversity of approaches, and non-generic detail for Creativity.\n"
        "- Keep rationale concise (2–4 sentences each).\n\n"
        "Output format (exactly these sections):\n"
        "Batch Evaluation\n"
        "Consistency: <brief rationale>\n"
        "Consistency Score: <integer 1-10>\n"
        "Creativity: <brief rationale>\n"
        "Creativity Score: <integer 1-10>\n"
    )
    return header + "\n".join(body_lines) + "\n" + footer


def evaluate_batch_with_gemini(
    pairs: List[Tuple[str, str]],
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.5
) -> Tuple[str, Dict[str, Optional[int]], str]:
    """
    Evaluate a batch of (input, answer) pairs for batch-level metrics.

    Returns: (feedback_text, {consistency, creativity}, prompt_text)
    """
    try:
        prompt = _build_batch_prompt(pairs)
        generation_config = {"temperature": temperature}
        model = genai.GenerativeModel(
            model_name,
            generation_config=generation_config
        )
        response = model.generate_content(prompt)
        feedback_text = response.text
        scores = {
            "consistency": extract_consistency_score(feedback_text),
            "creativity": extract_creativity_score(feedback_text),
        }
        return feedback_text, scores, prompt
    except Exception as e:
        error_msg = f"Error during batch evaluation: {str(e)}"
        prompt_for_error = _build_batch_prompt(pairs)
        return error_msg, {"consistency": None, "creativity": None}, prompt_for_error

def extract_rating(text: str) -> Optional[int]:
    """
    Extract the rating from the evaluation text.
    
    Args:
        text: The evaluation response text
    
    Returns:
        The rating as an integer or None if not found
    """
    # Look for patterns like "Total Rating: 3" or "Rating:** 3" or "Total Score: 8"
    patterns = [
        r'Total Score[:\s]*\*?\*?\s*(\d{1,2})',
        r'Total Rating[:\s]*\*?\*?\s*(\d{1,2})',
        r'Rating[:\s]*\*?\*?\s*(\d{1,2})',
        r'Score[:\s]*\*?\*?\s*(\d{1,2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            rating = int(match.group(1))
            if 1 <= rating <= 10:
                return rating
    
    return None


def extract_relevance_score(text: str) -> Optional[int]:
    """
    Extract the relevance score (1-10) from the evaluation text.
    
    Args:
        text: The evaluation response text
    
    Returns:
        The relevance score as an integer (1-10) or None if not found
    """
    match = re.search(r'Relevance Score[:\s-]*\*?\*?\s*(\d{1,2})', text, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        if 1 <= score <= 10:
            return score
    return None


def extract_clarity_score(text: str) -> Optional[int]:
    """
    Extract the clarity score (1-10) from the evaluation text.
    
    Args:
        text: The evaluation response text
    
    Returns:
        The clarity score as an integer (1-10) or None if not found
    """
    match = re.search(r'Clarity Score[:\s-]*\*?\*?\s*(\d{1,2})', text, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        if 1 <= score <= 10:
            return score
    return None


def extract_consistency_score(text: str) -> Optional[int]:
    """
    Extract the consistency score (1-10) from the evaluation text.
    """
    match = re.search(r'Consistency Score[:\s-]*\*?\*?\s*(\d{1,2})', text, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        if 1 <= score <= 10:
            return score
    return None


def extract_creativity_score(text: str) -> Optional[int]:
    """
    Extract the creativity score (1-10) from the evaluation text.
    """
    match = re.search(r'Creativity(?:/Innovation)? Score[:\s-]*\*?\*?\s*(\d{1,2})', text, re.IGNORECASE)
    if match:
        score = int(match.group(1))
        if 1 <= score <= 10:
            return score
    return None


def generate_with_llm(
    prompt: str,
    provider: str,
    model_name: str,
    temperature: float = 0.5,
    response_schema: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate content using a specified LLM provider.
    
    Args:
        prompt: The full prompt to send to the model
        provider: The LLM provider ('gemini' or 'openai')
        model_name: The specific model to use
        temperature: The generation temperature
        
    Returns:
        The generated text content
    """
    try:
        if provider == 'gemini':
            generation_config = {"temperature": temperature}
            if response_schema:
                generation_config["response_mime_type"] = "application/json"
                generation_config["response_schema"] = response_schema
            model = genai.GenerativeModel(
                model_name,
                generation_config=generation_config
            )
            response = model.generate_content(prompt)
            text = response.text
            if response_schema and text:
                # Try to extract a clean JSON object
                json_str = _extract_json_object(text)
                if json_str:
                    return json_str
            return text
        else:
            return f"Error: Unsupported provider '{provider}'"
            
    except Exception as e:
        return f"Error during generation: {str(e)}"