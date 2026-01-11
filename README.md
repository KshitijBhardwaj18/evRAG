# EvRAG - Production RAG Evaluation Platform

A comprehensive, production-grade SaaS platform for evaluating Retrieval-Augmented Generation (RAG) systems. Built for correctness, retrieval quality, hallucination detection, and observability.

## 🎯 Overview

EvRAG helps you evaluate your RAG pipelines with:

- **Comprehensive Retrieval Metrics**: Recall@K, Precision@K, MRR, MAP, Hit Rate, Coverage
- **Generation Quality Assessment**: Faithfulness, Answer Relevance, Context Utilization, Semantic Similarity
- **Multi-Signal Hallucination Detection**: LLM-as-Judge, Citation Check, Embedding Drift
- **Visual Dashboards**: Interactive charts and per-query breakdowns
- **Run Comparison**: Track improvements across evaluation runs
- **Extensible Architecture**: Easy to add new metrics and evaluators

## 🏗️ Architecture

```
EvRAG/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── evaluation/       # Core evaluation logic
│   │   │   ├── retrieval/   # Retrieval metrics
│   │   │   ├── generation/  # Generation metrics
│   │   │   └── hallucination/ # Hallucination detection
│   │   ├── db/              # Database models
│   │   ├── services/        # Business logic
│   │   └── rag/             # RAG pipeline interfaces
│   └── requirements.txt
│
└── frontend/         # Next.js frontend
    ├── app/                 # Pages
    ├── components/          # UI components
    └── lib/                 # API client & utils
```

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb evrag

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run server
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local if needed

# Run dev server
npm run dev
```

Frontend runs at: http://localhost:3000

## 📊 Evaluation Metrics

### Retrieval Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Recall@K** | Fraction of relevant docs in top K | `relevant_in_topK / total_relevant` |
| **Precision@K** | Fraction of top K that are relevant | `relevant_in_topK / K` |
| **MRR** | Mean Reciprocal Rank | `1 / rank_of_first_relevant` |
| **MAP** | Mean Average Precision | `Σ(Precision@k × relevance@k) / total_relevant` |
| **Hit Rate** | At least one relevant doc found | `1 if any relevant else 0` |
| **Coverage** | Fraction of GT retrieved | `GT_docs_retrieved / total_GT_docs` |

### Generation Metrics

| Metric | Description |
|--------|-------------|
| **Faithfulness** | Answer grounded in retrieved context |
| **Answer Relevance** | Answer addresses the query |
| **Context Utilization** | Answer uses retrieved information |
| **Semantic Similarity** | Similarity to ground truth answer |
| **ROUGE-L** | Longest common subsequence F-measure |
| **F1 Score** | Token-level precision & recall |

### Hallucination Detection

**Multi-Signal Approach:**

1. **LLM-as-Judge** (40% weight)
   - Uses GPT to identify unsupported claims
   - Fallback to rule-based detection

2. **Citation Check** (35% weight)
   - Each answer sentence must map to context
   - Reports uncited spans

3. **Embedding Drift** (25% weight)
   - Semantic distance between answer and context
   - High drift indicates hallucination

**Output:**
- Aggregated hallucination score (0-1)
- Highlighted hallucinated text spans
- Severity classification

## 📝 Dataset Format

### JSON
```json
{
  "items": [
    {
      "query": "What is retrieval-augmented generation?",
      "ground_truth_docs": ["doc1", "doc2"],
      "ground_truth_answer": "RAG combines retrieval with generation..."
    }
  ]
}
```

### CSV
```csv
query,ground_truth_docs,ground_truth_answer
"What is RAG?","[""doc1"", ""doc2""]","RAG is a technique..."
```

### JSONL
```jsonl
{"query": "What is RAG?", "ground_truth_docs": ["doc1"], "ground_truth_answer": "..."}
{"query": "How does RAG work?", "ground_truth_docs": ["doc2"], "ground_truth_answer": "..."}
```

## 🔌 RAG Pipeline Integration

Your RAG endpoint should accept:

```json
{
  "query": "user query text",
  "top_k": 5
}
```

And return:

```json
{
  "retrieved_docs": [
    {"id": "doc1", "text": "document content..."},
    {"id": "doc2", "text": "more content..."}
  ],
  "generated_answer": "The answer is..."
}
```

## 🎨 Screenshots & Features

### Dashboard
- Real-time evaluation progress
- Aggregate metrics visualization
- Per-query breakdown with drill-down

### Hallucination Detection
- Highlighted unsupported claims
- Multi-signal confidence scores
- Citation coverage tracking

### Run Comparison
- Side-by-side metrics
- Delta calculations
- Trend analysis

## 🛠️ Tech Stack

**Backend:**
- FastAPI (async API framework)
- PostgreSQL (data storage)
- SQLAlchemy (ORM)
- SentenceTransformers (embeddings)
- OpenAI (optional LLM judge)

**Frontend:**
- Next.js 14 (React framework)
- Tailwind CSS (styling)
- shadcn/ui (UI components)
- Recharts (data visualization)

## 📈 Usage Flow

1. **Upload Dataset**
   - CSV/JSON/JSONL with queries and ground truth
   - Validates schema on upload

2. **Create Evaluation Run**
   - Connect RAG API endpoint
   - Configure parameters

3. **Run Evaluation**
   - Async processing in background
   - Real-time progress tracking

4. **View Results**
   - Comprehensive metrics dashboard
   - Per-query analysis
   - Hallucination detection results

5. **Compare Runs**
   - Track improvements over time
   - Identify regressions

## 🧪 Testing

Use the mock RAG pipeline for testing without a real RAG system:

```python
# In evaluation creation, leave rag_endpoint empty
# System will use MockRAGPipeline
```

## 🔐 Security Notes

- No authentication implemented (add as needed)
- CORS configured for localhost (update for production)
- SQL injection protected via SQLAlchemy
- Input validation via Pydantic

## 📦 Deployment

### Backend (Docker example)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Vercel/Netlify)

```bash
npm run build
# Deploy dist/ folder
```

## 🤝 Contributing

This is a production-ready foundation. To extend:

1. **Add new metrics**: Create new files in `backend/app/evaluation/`
2. **Custom evaluators**: Implement in `evaluation/` modules
3. **UI enhancements**: Add components in `frontend/components/`

## 📄 License

MIT License - feel free to use in your projects

## 🎯 Roadmap

- [ ] Authentication & multi-tenancy
- [ ] Billing integration
- [ ] More LLM providers (Anthropic, Cohere)
- [ ] Batch evaluation API
- [ ] Custom metric definitions
- [ ] Export reports (PDF/CSV)
- [ ] Webhooks for run completion
- [ ] A/B testing framework

## 💡 Design Principles

1. **Correctness over speed**: Accurate metrics are critical
2. **Extensibility**: Easy to add new evaluators
3. **Production-ready**: Clean architecture, error handling, logging
4. **No unnecessary abstractions**: Pragmatic code structure
5. **Observable**: Track everything that matters

---

Built with ❤️ for the RAG community

