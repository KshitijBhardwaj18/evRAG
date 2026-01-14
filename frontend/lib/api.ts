import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Dataset {
  id: string
  name: string
  description?: string
  current_version: number
  total_items: number
  file_format?: string
  created_at: string
  updated_at?: string
}

export interface DatasetVersion {
  id: string
  dataset_id: string
  version_number: number
  changes_summary?: string
  item_count: number
  created_at: string
  created_by?: string
}

export interface DatasetItem {
  id: string
  dataset_id: string
  query: string
  ground_truth_docs?: any[]
  ground_truth_answer?: string
  metadata?: any
}

export interface EvaluationRun {
  id: string
  dataset_id: string
  name: string
  description?: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  rag_endpoint?: string
  rag_config?: any
  metrics?: any
  total_items: number
  completed_items: number
  error_message?: string
  created_at: string
  started_at?: string
  completed_at?: string
}

export interface EvaluationResult {
  id: string
  run_id: string
  dataset_item_id: string
  retrieved_docs?: any[]
  generated_answer?: string
  recall_at_k?: Record<number, number>
  precision_at_k?: Record<number, number>
  mrr?: number
  map_score?: number
  hit_rate?: number
  coverage?: number
  faithfulness?: number
  answer_relevance?: number
  context_utilization?: number
  semantic_similarity?: number
  rouge_l?: number
  f1_score?: number
  hallucination_score?: number
  hallucinated_spans?: string[]
  citation_coverage?: number
  metrics_detail?: any
  created_at: string
}

export const datasetApi = {
  list: () => api.get<Dataset[]>('/datasets'),
  get: (id: string) => api.get<Dataset & { items: DatasetItem[] }>(`/datasets/${id}`),
  create: (data: any) => api.post<Dataset>('/datasets', data),
  upload: (file: File, name?: string, description?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (name) formData.append('name', name)
    if (description) formData.append('description', description)
    
    return api.post<Dataset>('/datasets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  delete: (id: string) => api.delete(`/datasets/${id}`),
}

export const versionApi = {
  list: (datasetId: string) => api.get<DatasetVersion[]>(`/datasets/${datasetId}/versions`),
  get: (datasetId: string, versionNumber: number) => 
    api.get<DatasetVersion>(`/datasets/${datasetId}/versions/${versionNumber}`),
  create: (datasetId: string, changesSummary?: string) => 
    api.post<DatasetVersion>(`/datasets/${datasetId}/versions`, { changes_summary: changesSummary }),
  rollback: (datasetId: string, versionNumber: number) => 
    api.post(`/datasets/${datasetId}/versions/${versionNumber}/rollback`),
  compare: (datasetId: string, version1: number, version2: number) => 
    api.get(`/datasets/${datasetId}/versions/compare/${version1}/${version2}`),
}

export const evaluationApi = {
  list: (datasetId?: string) => 
    api.get<EvaluationRun[]>('/evaluations', { params: { dataset_id: datasetId } }),
  get: (id: string) => api.get<EvaluationRun>(`/evaluations/${id}`),
  create: (data: {
    dataset_id: string
    name: string
    description?: string
    rag_endpoint?: string
    rag_config?: any
  }) => api.post<EvaluationRun>('/evaluations', data),
  getResults: (id: string) => 
    api.get<EvaluationResult[]>(`/evaluations/${id}/results`),
  compare: (runId1: string, runId2: string) =>
    api.get(`/evaluations/compare/${runId1}/${runId2}`),
}


