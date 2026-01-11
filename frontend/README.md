# EvRAG Frontend

Modern Next.js frontend for the RAG Evaluation Platform.

## Features

- 📊 **Interactive Dashboards**: Real-time visualization of evaluation metrics
- 📈 **Charts & Graphs**: Recharts-powered data visualization
- 🎯 **Per-Query Analysis**: Drill down into individual query results
- ⚖️ **Run Comparison**: Side-by-side comparison of evaluation runs
- 🎨 **Modern UI**: Built with Tailwind CSS and shadcn/ui components
- 🚀 **Fast & Responsive**: Next.js 14 with App Router

## Setup

### Prerequisites

- Node.js 18+
- Backend API running (see backend README)

### Installation

```bash
# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local
# Edit .env.local with your backend API URL

# Run development server
npm run dev
```

The app will be available at http://localhost:3000

### Production Build

```bash
npm run build
npm start
```

## Pages

- `/` - Home page with feature overview
- `/datasets` - Dataset management and upload
- `/datasets/[id]` - Dataset details and evaluation creation
- `/runs` - List of all evaluation runs
- `/runs/[id]` - Detailed run results with metrics
- `/runs/compare` - Side-by-side run comparison

## Features

### Dataset Upload
Upload CSV, JSON, or JSONL files with:
- Query text
- Ground truth documents
- Ground truth answer (optional)

### Evaluation Metrics Visualization
- **Retrieval**: Recall@K, Precision@K, MRR, MAP
- **Generation**: Faithfulness, Answer Relevance, Context Utilization
- **Hallucination**: Aggregated score with highlighted spans
- **Charts**: Bar charts, radar charts, progress tracking

### Run Comparison
- Side-by-side metric comparison
- Delta calculations with % improvement
- Visual indicators for improvements/regressions

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **UI Components**: shadcn/ui (Radix UI)
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Development

```bash
# Run dev server with hot reload
npm run dev

# Type checking
npm run build

# Lint
npm run lint
```

## API Integration

The frontend connects to the FastAPI backend via the API client in `lib/api.ts`.

Default API URL: http://localhost:8000/api

Configure via `NEXT_PUBLIC_API_URL` environment variable.

## Component Structure

```
app/                    # Next.js pages (App Router)
  ├── page.tsx         # Home
  ├── datasets/        # Dataset pages
  ├── runs/            # Evaluation run pages
  └── globals.css      # Global styles

components/
  └── ui/              # shadcn/ui components

lib/
  ├── api.ts           # API client
  └── utils.ts         # Utilities
```

## License

MIT

