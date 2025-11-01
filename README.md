# 🧾 LLM Evaluation Playground

A Streamlit web app for generating educational intervention and curriculum prompts, evaluating model-generated outputs using LLM-as-a-Judge evaluation, and validating responses with Pydantic.

## 🎯 Features

- **Intervention Prompt Generation** – Generate targeted intervention plans based on EMT (Emotion Matching Task) scores
- **Curriculum Prompt Generation** – Create personalized curriculum-based intervention plans
- **LLM-as-a-Judge Evaluation** – Uses Google Gemini API to evaluate answer quality with detailed scoring
- **Multi-Metric Scoring** – Evaluates answers across 5 dimensions: Total, Relevance, Clarity, Consistency, and Creativity (1-10 scale)
- **Separate Generator & Judge Models** – Configure different models and temperatures for generation vs. evaluation
- **Pydantic Validation** – Validates structural completeness of answers
- **CSV Logging** – Automatically logs all evaluations to CSV with comprehensive metrics
- **Evaluation History** – View past evaluations with summary statistics
- **Batch Evaluation** – Process multiple evaluations from a CSV file
- **Multiple Models** – Support for Gemini 2.5 models (Pro, Flash, Flash-Lite)

## 🚀 Setup

### 1. Clone or navigate to the project directory

```bash
cd llm-judge
```

### 2. Create a virtual environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your Google API key:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

**To get a Google API key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste it into your `.env` file

### 5. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage

### Individual Evaluation

1. **Enter your API key** in the sidebar (or set it in `.env` file)

2. **Configure models**:
   - Select a **Judge Model** for evaluation (with temperature control)
   - Select a **Generator Model** for answer generation (with temperature control)

3. **Select prompt type**:
   - **EMT (Emotion Matching Task)**: Generate intervention plans based on class performance scores
   - **Curriculum**: Generate curriculum-based interventions based on grade level and skill areas

4. **Enter JSON input data**:
   - **For EMT**: Provide scores and metadata (see example format below)
   - **For Curriculum**: Provide grade level, skill areas, and score

5. **Click "Generate & Evaluate"** to:
   - Generate the intervention/curriculum prompt
   - Generate the answer using the selected generator model
   - Evaluate the answer using the LLM judge

6. **View results**:
   - Generated prompt (Step 2)
   - Generated answer (Step 3)
   - **Evaluation metrics**:
     - Total Rating (1-10)
     - Relevance Score (1-10)
     - Clarity Score (1-10)
     - Consistency Score (1-10)
     - Creativity Score (1-10)
   - Pydantic validation status
   - Detailed LLM judge feedback

7. **Check history** by toggling "Show Evaluation History" to view all past evaluations with summary statistics

### Batch Evaluation

1. **Prepare CSV file** with the following columns:
   - `type`: Either "emt" or "curriculum"
   - `input`: JSON string containing the input data

2. See `sample-input-dataset.csv` for example format

3. **Upload CSV** in the "Batch Evaluation" tab

4. **Click "Run Batch Evaluation"** to process all rows

5. **Download results** as CSV with all evaluation metrics

### Example Input Formats

**EMT Input:**
```json
{
  "scores": {
    "EMT1": [35.0, 40.0, 38.0, 42.0, 39.0],
    "EMT2": [75.0, 78.0, 80.0, 77.0, 79.0],
    "EMT3": [70.0, 72.0, 68.0, 71.0, 69.0],
    "EMT4": [65.0, 67.0, 70.0, 68.0, 66.0]
  },
  "metadata": {
    "class_id": "QUICK_TEST_1A",
    "deficient_area": "EMT1",
    "num_students": 25
  }
}
```

**Curriculum Input:**
```json
{
  "grade_level": "1",
  "skill_areas": ["emotional_awareness"],
  "score": 25.0
}
```

## 🤖 Gemini 2.5 Models

The app supports three Gemini 2.5 models, each optimized for different use cases:

### **Gemini 2.5 Pro** (`gemini-2.5-pro`)
- **Best for**: Complex tasks requiring detailed analysis
- **Strengths**: 
  - Handles large datasets
  - Long context windows (over 1 million tokens)
  - Provides comprehensive, detailed responses
- **Use cases**: Long-form content, research summaries, advanced coding help

### **Gemini 2.5 Flash** (`gemini-2.5-flash`) ⚡ *Recommended*
- **Best for**: Balanced performance and quality
- **Strengths**: 
  - Optimized for speed and cost-efficiency
  - Low latency responses
  - Good quality-to-speed ratio
- **Use cases**: Real-time applications, chat, summarization, interactive experiences

### **Gemini 2.5 Flash-Lite** (`gemini-2.5-flash-lite`)
- **Best for**: High-volume, high-speed tasks
- **Strengths**: 
  - Fastest model in the 2.5 series
  - Most cost-effective option
  - High throughput
- **Use cases**: Classification, sentiment analysis, high-scale operations

## 📊 CSV Output

All evaluations are automatically saved to `evaluations.csv` with the following columns:

- `timestamp` – When the evaluation was performed
- `model` – Which generator model was used
- `temperature` – Temperature setting for the generator model
- `question` – The input context/question (prompt type and input data)
- `answer` – The model-generated answer
- `judge_feedback` – Detailed feedback from the LLM judge
- `judge_prompt` – The prompt sent to the LLM judge
- `total_rating(1-10)` – Overall rating from 1-10
- `validation_status` – Pydantic validation result (Valid ✅ or Invalid ❌)
- `relevance_score` – Relevance score from 1-10
- `clarity_score` – Clarity score from 1-10
- `consistency_score` – Consistency score from 1-10
- `creativity_score` – Creativity score from 1-10

## 🏗️ Project Structure

```
llm-judge/
├── app.py                  # Main Streamlit application
├── judge.py                # LLM-as-a-Judge evaluation logic
├── models.py               # Pydantic models for validation
├── logger.py               # CSV logging functionality
├── intervention.py         # Intervention prompt generation
├── curriculum.py           # Curriculum prompt generation
├── schemas/                # Pydantic schema definitions
│   ├── base.py            # Intervention plan schema
│   └── curriculum.py      # Curriculum response schema
├── requirements.txt        # Python dependencies
├── evaluations.csv         # Evaluation log (generated)
├── sample-input-dataset.csv # Example CSV for batch evaluation
├── .env.example           # Example environment file
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── PRD.md                 # Product requirements document
```

## 🛠️ Customization

### Modify the Judge Prompt

Edit the `EVALUATION_PROMPT` in `judge.py` to customize evaluation criteria and scoring dimensions.

### Change Validation Schema

Update the `ModelAnswer` class in `models.py` to match your expected answer structure.

### Customize Intervention Prompts

Modify `InterventionPrompt` class in `intervention.py` to:
- Update EMT strategies
- Change the base prompt template
- Adjust safety guidelines

### Customize Curriculum Prompts

Modify `CurriculumPrompt` class in `curriculum.py` to:
- Update available interventions
- Change curriculum data
- Adjust prompt templates

### Add New Models

Add more Gemini models to the `model_options` dictionary in `app.py` (sidebar section).

### Modify Evaluation Metrics

Update the `EVALUATION_PROMPT` in `judge.py` and the score extraction functions to add or modify evaluation dimensions.

## 📝 License

MIT License - feel free to use and modify as needed.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
