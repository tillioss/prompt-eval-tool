# 🧾 PRD: LLM Evaluation Playground (Python + Streamlit + Pydantic)

## 🎯 Goal
Evaluate two SEAL prompts in two modes: single run and batch run (5 input-output pairs). Provide qualitative scoring via LLM-as-a-Judge and binary completeness via structured output (primary) and Pydantic (fallback). Log results to CSV with per-item and batch-level metrics.

---

## 🧱 Tech Stack

| Layer | Tool |
|--------|------|
| Frontend | Streamlit |
| Backend | Python |
| Model | Google Gemini API |
| Validation | Pydantic + Gemini Structured Output (optional) |
| Data Logging | CSV (`pandas`) |
| Environment | `.env` for `GOOGLE_API_KEY` |

---

## ⚙️ Features

### Modes
- Single Run (Prompt A): Judge Relevance and Clarity on 1–10 scale
- Batch Run (5 pairs): Per-item Relevance and Clarity; Batch-level Consistency and Creativity (1–10)

### Single Run
- Inputs: Prompt type (emt/curriculum), JSON input
- Outputs: Generated prompt, generated answer, judge feedback
- Scores: Relevance (1–10), Clarity (1–10), Total (1–10)
- Completeness: Structured output (if enabled) or Pydantic validation

### Batch Run (5 datasets)
- Inputs: CSV with 5 rows (columns: `type`, `input` JSON)
- Per-item Scores: Relevance (1–10), Clarity (1–10)
- Batch Scores: Consistency (1–10), Creativity (1–10)
- Completeness: Structured output (if enabled) or Pydantic validation

---

## 🧩 Data Logging to CSV

Stored in `evaluations.csv` and appended after every run.

Columns:

- `timestamp` – Time of evaluation
- `batch_id` – Identifier for batch runs (same for all rows in a batch)
- `row_type` – `item` for per-item rows, `batch_summary` for the batch metrics row
- `model` – Generator model used
- `temperature` – Generator temperature
- `question` – Input context (prompt type + input data)
- `answer` – Generated output
- `judge_feedback` – Feedback text
- `judge_prompt` – Prompt used for judging
- `total_rating(1-10)` – Overall score (1–10)
- `validation_status` – Pydantic result or `Valid (Structured Output)`
- `relevance_score` – 1–10
- `clarity_score` – 1–10
- `consistency_score` – 1–10 (batch_summary only)
- `creativity_score` – 1–10 (batch_summary only)

---

## 📁 File Structure

Unchanged from README, plus `schemas/` containing Pydantic models for structured output.

---

## 📏 Evaluation Criteria

### Single Run (Prompt A)
- Relevance (1–10)
- Clarity (1–10)
- Total Score (1–10 average)

### Batch Run (5 datasets)
- Per-item: Relevance (1–10), Clarity (1–10)
- Batch-level: Consistency (1–10), Creativity (1–10)

Batch-level evaluation prompt:

```
Following are the inputs and answer combinations for prompt 1

{input1} : {answer1}
{input2} : {answer2}
{input3} : {answer3}
{input4} : {answer4}
{input5} : {answer5}

Please evaluate and score these results for consistency and creativity

Consistency means..., how to score
Creativity means ..., how to score
```

---

## ✅ Acceptance Criteria

- README and PRD document single vs batch evaluation, criteria, and logging
- Batch run shows per-item Relevance/Clarity and a single Consistency/Creativity metric
- CSV contains per-item rows and one batch summary row per batch with `batch_id`
- Structured Output toggle works; if enabled, Pydantic check can be bypassed

