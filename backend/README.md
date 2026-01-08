# EvRAG Backend

Production-grade RAG Evaluation Platform - Backend API

## Features

- **Comprehensive Retrieval Metrics**: Recall@K, Precision@K, MRR, MAP, Hit Rate, Coverage
- **Generation Quality Metrics**: Faithfulness, Answer Relevance, Context Utilization, Semantic Similarity, ROUGE-L, F1
- **Multi-Signal Hallucination Detection**: LLM-as-Judge, Citation Check, Embedding Drift
- **Dataset Management**: Upload CSV/JSON/JSONL datasets
- **Run Comparison**: Compare evaluation runs over time
- **Async Evaluation**: Background processing for long-running evaluations

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis (optional, for Celery)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup

```bash
# Create database
createdb evrag

# Run migrations (if using Alembic)
alembic upgrade head
```

### Run Server

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

```
app/
├── api/           # API routes
├── core/          # Configuration and logging
├── db/            # Database models and session
├── evaluation/    # Core evaluation logic
│   ├── retrieval/      # Retrieval metrics
│   ├── generation/     # Generation metrics
│   ├── hallucination/  # Hallucination detection
│   └── runner.py       # Orchestration
├── rag/           # RAG pipeline interfaces
├── schemas/       # Pydantic schemas
└── services/      # Business logic
```

## Evaluation Metrics

### Retrieval
- **Recall@K**: Fraction of relevant docs in top K
- **Precision@K**: Fraction of top K that are relevant
- **MRR**: Mean Reciprocal Rank
- **MAP**: Mean Average Precision
- **Hit Rate**: At least one relevant doc retrieved
- **Coverage**: Fraction of ground truth retrieved

### Generation
- **Faithfulness**: Answer grounded in context
- **Answer Relevance**: Answer addresses question
- **Context Utilization**: Answer uses retrieved context
- **Semantic Similarity**: Similarity to ground truth answer
- **ROUGE-L**: LCS-based metric
- **F1 Score**: Token-level F1

### Hallucination Detection
- **LLM-as-Judge**: GPT evaluation of claims
- **Citation Check**: Each sentence has citation
- **Embedding Drift**: Semantic distance from context
- **Aggregated Score**: Weighted combination

## Usage Example

```python
# Upload dataset
POST /api/datasets/upload
Content-Type: multipart/form-data
file: dataset.json

# Create evaluation run
POST /api/evaluations
{
  "dataset_id": "...",
  "name": "Baseline Run",
  "rag_endpoint": "http://localhost:5000/query"
}

# Get results
GET /api/evaluations/{run_id}

# Compare runs
GET /api/evaluations/compare/{run1_id}/{run2_id}
```

## Dataset Format

### JSON
```json
{
  "items": [
    {
      "query": "What is RAG?",
      "ground_truth_docs": ["doc1", "doc2"],
      "ground_truth_answer": "RAG is Retrieval-Augmented Generation..."
    }
  ]
}
```

### CSV
```csv
query,ground_truth_docs,ground_truth_answer
"What is RAG?","[""doc1"", ""doc2""]","RAG is..."
```

## License

MIT

