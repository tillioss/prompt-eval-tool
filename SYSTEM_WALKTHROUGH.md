# 🏗️ LLM Evaluation Playground - Complete System Walkthrough

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture & Components](#architecture--components)
3. [Data Flow](#data-flow)
4. [Key Modules Deep Dive](#key-modules-deep-dive)
5. [User Workflows](#user-workflows)
6. [Evaluation Metrics](#evaluation-metrics)
7. [Data Storage](#data-storage)

---

## 🎯 System Overview

**Purpose:** Evaluate the quality of AI-generated educational intervention prompts using LLM-as-a-Judge methodology.

**Core Function:** 
- Generate educational intervention/curriculum prompts
- Evaluate generated answers using an LLM judge
- Validate answers using Pydantic
- Log all evaluations to CSV for analysis

**Tech Stack:**
- **Frontend:** Streamlit (web UI)
- **Backend:** Python 3.9+
- **LLM:** Google Gemini API (2.5 Pro/Flash/Flash-Lite)
- **Validation:** Pydantic
- **Data:** CSV logging with pandas

---

## 🏛️ Architecture & Components

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Individual   │  │   Batch      │  │   History    │      │
│  │  Evaluation  │  │  Evaluation  │  │    Viewer    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │      Prompt Generation Layer          │
        │  ┌──────────────┐  ┌──────────────┐  │
        │  │ Intervention │  │  Curriculum │  │
        │  │   Prompt     │  │   Prompt    │  │
        │  └──────────────┘  └──────────────┘  │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │      LLM Generation (judge.py)        │
        │  ┌──────────────┐  ┌──────────────┐  │
        │  │  Generator   │  │    Judge    │  │
        │  │    Model     │  │    Model    │  │
        │  └──────────────┘  └──────────────┘  │
        └───────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │      Validation & Logging            │
        │  ┌──────────────┐  ┌──────────────┐  │
        │  │   Pydantic   │  │     CSV      │  │
        │  │  Validation  │  │   Logger    │  │
        │  └──────────────┘  └──────────────┘  │
        └───────────────────────────────────────┘
```

### Component Breakdown

#### 1. **Frontend Layer** (`app.py`)
- Streamlit web interface
- User input collection
- Results display
- Configuration management

#### 2. **Prompt Generation** (`prompts/`)
- **`intervention.py`**: EMT-based intervention prompts
- **`curriculum.py`**: Curriculum-based intervention prompts
- **`__init__.py`**: Package initialization file

#### 3. **LLM Integration** (`judge.py`)
- Generator: Creates answers from prompts
- Judge: Evaluates answer quality
- Score extraction: Parses scores from judge responses

#### 4. **Validation** (`models.py`)
- Pydantic models for answer validation
- Completeness checking

#### 5. **Logging** (`logger.py`)
- CSV persistence
- History retrieval
- Batch summary logging

#### 6. **Schemas** (`schemas/`)
- Pydantic schemas for structured output
- JSON schema generation for prompts

---

## 🔄 Data Flow

### Individual Evaluation Flow

```
User Input (JSON)
    │
    ▼
┌─────────────────────────────────────┐
│  1. Parse Input Data               │
│     - EMT scores + metadata        │
│     - OR curriculum data           │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  2. Generate Prompt                 │
│     - InterventionPrompt.get_prompt │
│     - OR CurriculumPrompt.get_prompt │
│     - Includes schema + data        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  3. Generate Answer                 │
│     - generate_with_llm()           │
│     - Uses Generator Model          │
│     - Temperature controlled        │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  4. Validate Answer                │
│     - ModelAnswer(content=answer)   │
│     - Pydantic validation           │
│     - Returns Valid/Invalid         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  5. Evaluate Answer                 │
│     - evaluate_with_gemini()        │
│     - Uses Judge Model              │
│     - Extracts scores (1-10)         │
│     - Relevance & Clarity            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  6. Log Results                     │
│     - log_evaluation()              │
│     - CSV append                    │
│     - All metrics saved             │
└─────────────────────────────────────┘
```

### Batch Evaluation Flow

```
CSV File (5 rows)
    │
    ▼
┌─────────────────────────────────────┐
│  For each row:                     │
│    - Parse input JSON               │
│    - Generate prompt                 │
│    - Generate answer                 │
│    - Evaluate (Relevance/Clarity)   │
│    - Log per-item row                │
│    - Collect (input, answer) pairs  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Batch-Level Evaluation             │
│    - evaluate_batch_with_gemini()   │
│    - All pairs together             │
│    - Consistency & Creativity       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Log Batch Summary                  │
│    - log_batch_summary()            │
│    - Single row with batch metrics  │
│    - Same batch_id as items          │
└─────────────────────────────────────┘
```

---

## 🔍 Key Modules Deep Dive

### 1. `app.py` - Streamlit Application

**Responsibilities:**
- UI rendering and user interaction
- Configuration management (API keys, models, temperatures)
- Orchestrating the evaluation workflow
- Displaying results and history

**Key Sections:**
- **Sidebar:** Configuration (API key, models, temperatures)
- **Individual Tab:** Single evaluation workflow
- **Batch Tab:** CSV batch processing
- **History Section:** View past evaluations

**Notable Code Patterns:**
```python
# EMT data processing
scores = input_data.get('scores', {})
emt_averages = {k: sum(v) / len(v) for k, v in scores.items() if v}

# Prompt generation based on type
if prompt_type == 'emt':
    prompt = InterventionPrompt.get_prompt(generator_provider, prompt_data)
elif prompt_type == 'curriculum':
    prompt = CurriculumPrompt.get_prompt(generator_provider, input_data)
```

---

### 2. `prompts/intervention.py` - Intervention Prompt Generator

**Purpose:** Generate prompts for EMT-based educational interventions

**Key Components:**
- **EMT_STRATEGIES:** Dictionary of strategies for each EMT area (EMT1-EMT4)
- **BASE_TEMPLATE:** Main prompt template with safety guidelines
- **GEMINI_TEMPLATE:** Gemini-specific template variant
- **EXAMPLE_RESPONSE:** Example JSON structure for guidance

**Workflow:**
1. Takes input data (class_id, num_students, deficient_area, EMT averages)
2. Looks up strategies for deficient_area
3. Formats strategies into readable text
4. Embeds JSON schema from `schemas.base.InterventionPlan`
5. Formats template with all data
6. Returns complete prompt string

**Example Output Structure:**
```
- Safety guidelines
- Class information
- Current performance (EMT scores)
- Targeted strategies for deficient area
- Instructions
- JSON schema
- Example response
```

---

### 3. `prompts/curriculum.py` - Curriculum Prompt Generator

**Purpose:** Generate prompts for curriculum-based interventions

**Key Components:**
- **CURRICULUM_DATA:** List of 10 available interventions
- **BASE_TEMPLATE:** Main prompt template
- **GEMINI_TEMPLATE:** Gemini-specific variant

**Workflow:**
1. Takes input data (grade_level, skill_areas, score)
2. Formats skill_areas list into comma-separated string
3. Embeds curriculum data and JSON schema
4. Formats template
5. Returns complete prompt string

**Key Features:**
- Grade-level appropriate interventions
- Skill area focus (emotional_awareness, emotional_regulation, anger_management)
- Score-based recommendations

---

### 4. `judge.py` - LLM Integration & Evaluation

**Core Functions:**

#### **Generation Functions:**
- `generate_with_llm()`: Generates answers from prompts
- Supports Gemini provider
- Handles structured output (optional, not recommended)

#### **Evaluation Functions:**
- `evaluate_with_gemini()`: Individual evaluation
  - Uses `EVALUATION_PROMPT_INDIVIDUAL`
  - Extracts Relevance & Clarity scores
  - Returns feedback text and scores

- `evaluate_batch_with_gemini()`: Batch evaluation
  - Uses custom batch prompt
  - Evaluates Consistency & Creativity across pairs
  - Returns batch-level metrics only

#### **Score Extraction:**
- `extract_rating()`: Total score
- `extract_relevance_score()`: Relevance (1-10)
- `extract_clarity_score()`: Clarity (1-10)
- `extract_consistency_score()`: Consistency (1-10)
- `extract_creativity_score()`: Creativity (1-10)

**Evaluation Prompts:**
- **Individual:** Focuses on Relevance & Clarity
- **Batch:** Focuses on Consistency & Creativity across all pairs

---

### 5. `models.py` - Pydantic Validation

**Purpose:** Validate structural completeness of generated answers

**Models:**
- **ModelAnswer:** Validates answer has non-empty content
  - `content: str` (min_length=1)
  - `reasoning: Optional[str]`
  - Allows extra fields

- **EvaluationResult:** (Currently unused but defined)

**Validation Flow:**
```python
try:
    ModelAnswer(content=answer)
    validation_status = "Valid ✅"
except ValidationError as e:
    validation_status = f"Invalid ❌\n{str(e)}"
```

---

### 6. `logger.py` - CSV Logging

**Purpose:** Persist all evaluation data to CSV

**Key Functions:**
- `log_evaluation()`: Log individual or per-item evaluation
- `log_batch_summary()`: Log batch-level metrics
- `get_evaluation_history()`: Retrieve all past evaluations

**CSV Structure:**
- **Columns:** timestamp, batch_id, row_type, model, temperature, question, answer, judge_feedback, judge_prompt, total_rating(1-10), validation_status, relevance_score, clarity_score, consistency_score, creativity_score
- **Row Types:**
  - `item`: Individual or per-item batch evaluation
  - `batch_summary`: Batch-level metrics only

**Data Flow:**
1. Creates/reads CSV file
2. Appends new row with all metrics
3. Maintains column order
4. Handles missing columns gracefully

---

### 7. `schemas/` - JSON Schemas

**Purpose:** Define structure for LLM-generated responses

**Files:**
- **`base.py`:** InterventionPlan schema
  - Analysis, strategies, timeline, success_metrics
  - Used by InterventionPrompt

- **`curriculum.py`:** CurriculumResponse schema
  - Recommended interventions, skill focus, implementation order
  - Used by CurriculumPrompt

**Usage:**
- Schemas are converted to JSON Schema format
- Embedded in prompts to guide LLM output structure
- Not used for validation (Pydantic handles that)

---

## 👤 User Workflows

### Workflow 1: Individual Evaluation

1. **Setup:**
   - Enter API key in sidebar
   - Select Judge Model (e.g., gemini-2.5-flash)
   - Select Generator Model
   - Set temperatures

2. **Input:**
   - Select prompt type (EMT or Curriculum)
   - Enter JSON input data
   - Click "Generate & Evaluate"

3. **Processing:**
   - System generates prompt
   - Generates answer using Generator Model
   - Validates answer with Pydantic
   - Evaluates answer with Judge Model

4. **Output:**
   - View generated prompt
   - View generated answer
   - View evaluation scores (Relevance, Clarity)
   - View validation status
   - Results saved to CSV

---

### Workflow 2: Batch Evaluation

1. **Prepare CSV:**
   - Create CSV with `type` and `input` columns
   - Each row = one evaluation
   - See `sample-input-dataset.csv`

2. **Process:**
   - Upload CSV in Batch tab
   - Click "Run Batch Evaluation"
   - System processes each row

3. **Per-Item Processing:**
   - Generate prompt
   - Generate answer
   - Evaluate (Relevance & Clarity)
   - Log per-item row

4. **Batch-Level Evaluation:**
   - After all items processed
   - Evaluate Consistency & Creativity
   - Log batch summary row

5. **Output:**
   - Download results CSV
   - View batch metrics
   - All data saved to `evaluations.csv`

---

### Workflow 3: View History

1. **Toggle History:**
   - Check "Show Evaluation History" in sidebar
   - History section appears at bottom

2. **View Metrics:**
   - Total evaluations count
   - Average ratings
   - Validation success rate
   - Average scores by dimension

3. **View Data:**
   - Full evaluation table
   - Download CSV
   - Filter and analyze

---

## 📊 Evaluation Metrics

### Individual Mode Metrics

1. **Relevance (1-10):**
   - How relevant is the answer to the input?
   - 1 = Completely irrelevant
   - 10 = Perfectly relevant

2. **Clarity (1-10):**
   - How clear and understandable?
   - 1 = Incoherent
   - 10 = Perfectly clear

3. **Total Score (1-10):**
   - Average of Relevance and Clarity

4. **Validation Status:**
   - Valid ✅: Passes Pydantic validation
   - Invalid ❌: Fails validation

---

### Batch Mode Metrics

**Per-Item:**
- Relevance (1-10)
- Clarity (1-10)

**Batch-Level:**
- **Consistency (1-10):**
  - How consistent across multiple runs?
  - No contradictions, stable tone/format
  - 1 = Highly inconsistent
  - 10 = Perfectly consistent

- **Creativity (1-10):**
  - How original/innovative?
  - Avoids generic templates
  - 1 = Plagiarized/unoriginal
  - 10 = Highly original

---

## 💾 Data Storage

### CSV File: `evaluations.csv`

**Structure:**
```
timestamp | batch_id | row_type | model | temperature | question | answer | 
judge_feedback | judge_prompt | total_rating(1-10) | validation_status | 
relevance_score | clarity_score | consistency_score | creativity_score
```

**Row Types:**
- **`item`:** Individual evaluation or per-item batch evaluation
  - Has question, answer, relevance, clarity
  - May have batch_id if part of batch

- **`batch_summary`:** Batch-level metrics only
  - Has consistency_score, creativity_score
  - Has batch_id matching items
  - Empty question/answer fields

**Example:**
```csv
timestamp,batch_id,row_type,model,temperature,question,answer,...
2024-01-01 10:00:00,123456,item,gemini-2.5-flash,0.5,"Prompt Type: emt...","{...}",...
2024-01-01 10:00:01,123456,item,gemini-2.5-flash,0.5,"Prompt Type: emt...","{...}",...
2024-01-01 10:00:02,123456,batch_summary,gemini-2.5-flash,0.5,,,...
```

---

## 🔧 Configuration Points

### Models
- **Gemini 2.5 Pro:** Complex tasks, detailed analysis
- **Gemini 2.5 Flash:** ⚡ Recommended - Balanced speed/quality
- **Gemini 2.5 Flash-Lite:** High-speed, cost-effective

### Temperature
- **Judge:** 0.0-1.0 (default 0.5)
  - Lower = more consistent scoring
  - Higher = more varied feedback

- **Generator:** 0.0-1.0 (default 0.5)
  - Lower = more deterministic
  - Higher = more creative

### Prompt Customization
- **Intervention Prompts:** Edit `prompts/intervention.py`
  - Modify EMT_STRATEGIES
  - Update BASE_TEMPLATE
  - Adjust safety guidelines

- **Curriculum Prompts:** Edit `prompts/curriculum.py`
  - Update CURRICULUM_DATA
  - Modify templates

- **Judge Prompts:** Edit `judge.py`
  - `EVALUATION_PROMPT_INDIVIDUAL` - Used for individual evaluations (Relevance & Clarity)
  - `EVALUATION_PROMPT_BATCH_GUIDE` - Used for batch-level evaluations (Consistency & Creativity)
  - `EVALUATION_PROMPT` - Available but not currently used (fallback for non-individual mode)

---

## 🎯 Key Design Decisions

### 1. **Separate Generator & Judge Models**
- Allows different models for different purposes
- Generator can be creative, Judge can be analytical
- Independent temperature control

### 2. **Pydantic Validation (Not Structured Output)**
- Structured Output unreliable with Gemini
- Pydantic provides consistent validation
- More flexible error handling

### 3. **CSV Logging**
- Simple, human-readable format
- Easy to analyze in Excel/Python
- Append-only for durability

### 4. **Batch ID System**
- Links per-item rows to batch summary
- Enables batch-level analysis
- Maintains data integrity

### 5. **Two Prompt Types**
- **EMT:** Score-based, class-level interventions
- **Curriculum:** Grade-level, skill-based interventions
- Different use cases, same evaluation framework

---

## 🚀 Extension Points

### Adding New Prompt Types
1. Create new prompt class in `prompts/`
2. Add prompt type to `app.py` selectbox
3. Add processing logic in individual/batch tabs

### Adding New Evaluation Metrics
1. Update evaluation prompts in `judge.py`
2. Add extraction function
3. Update score extraction in `evaluate_with_gemini()`
4. Update CSV header in `logger.py`
5. Update UI display in `app.py`

### Adding New LLM Providers
1. Extend `generate_with_llm()` in `judge.py`
2. Add provider-specific logic
3. Update UI selectbox

### Custom Validation Schemas
1. Update `ModelAnswer` in `models.py`
2. Adjust validation in `app.py`
3. Update error handling

---

## 📝 Summary

The LLM Evaluation Playground is a comprehensive system for:

1. **Generating** educational intervention prompts (EMT or Curriculum)
2. **Generating** answers using LLM models
3. **Evaluating** answer quality using LLM-as-a-Judge
4. **Validating** structural completeness with Pydantic
5. **Logging** all results to CSV for analysis

**Key Strengths:**
- Modular architecture
- Flexible prompt types
- Comprehensive evaluation metrics
- Persistent data logging
- User-friendly Streamlit interface

**Use Cases:**
- Educational intervention design
- LLM prompt evaluation
- Quality assurance for AI-generated content
- Batch evaluation workflows
- Research and analysis

---

This system provides a complete evaluation framework for educational AI applications, with robust logging, validation, and analysis capabilities.

