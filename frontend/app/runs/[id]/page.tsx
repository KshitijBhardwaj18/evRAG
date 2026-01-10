"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { evaluationApi, type EvaluationRun, type EvaluationResult } from "@/lib/api"
import { ArrowLeft, AlertTriangle } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

export default function RunDetailPage() {
  const params = useParams()
  const runId = params.id as string
  
  const [run, setRun] = useState<EvaluationRun | null>(null)
  const [results, setResults] = useState<EvaluationResult[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedResult, setSelectedResult] = useState<EvaluationResult | null>(null)

  useEffect(() => {
    loadRun()
    loadResults()
    
    const interval = setInterval(() => {
      loadRun()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [runId])

  const loadRun = async () => {
    try {
      const response = await evaluationApi.get(runId)
      setRun(response.data)
    } catch (error) {
      console.error("Failed to load run:", error)
    } finally {
      setLoading(false)
    }
  }

  const loadResults = async () => {
    try {
      const response = await evaluationApi.getResults(runId)
      setResults(response.data)
    } catch (error) {
      console.error("Failed to load results:", error)
    }
  }

  if (loading || !run) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p>Loading run...</p>
      </div>
    )
  }

  // Prepare chart data
  const recallData = [
    { k: 1, value: (run.metrics?.avg_recall_at_1 || 0) * 100 },
    { k: 3, value: (run.metrics?.avg_recall_at_3 || 0) * 100 },
    { k: 5, value: (run.metrics?.avg_recall_at_5 || 0) * 100 },
    { k: 10, value: (run.metrics?.avg_recall_at_10 || 0) * 100 },
  ]

  const radarData = [
    { metric: 'Faithfulness', value: (run.metrics?.avg_faithfulness || 0) * 100 },
    { metric: 'Relevance', value: (run.metrics?.avg_answer_relevance || 0) * 100 },
    { metric: 'Utilization', value: (run.metrics?.avg_context_utilization || 0) * 100 },
    { metric: 'MRR', value: (run.metrics?.avg_mrr || 0) * 100 },
    { metric: 'MAP', value: (run.metrics?.avg_map_score || 0) * 100 },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="border-b bg-white">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/runs" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-4 w-4" />
            Back to Runs
          </Link>
          <h1 className="text-2xl font-bold">{run.name}</h1>
          <div className="w-24" />
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Overview Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Avg Recall@5</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {((run.metrics?.avg_recall_at_5 || 0) * 100).toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Avg Faithfulness</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {((run.metrics?.avg_faithfulness || 0) * 100).toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Hallucination Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-red-600">
                {((run.metrics?.hallucination_rate || 0) * 100).toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">Avg MRR</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {(run.metrics?.avg_mrr || 0).toFixed(3)}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Recall@K</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={recallData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="k" label={{ value: 'K', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'Recall (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Overall Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <PolarRadiusAxis domain={[0, 100]} />
                  <Radar name="Score" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Per-Query Results */}
        <Card>
          <CardHeader>
            <CardTitle>Per-Query Results</CardTitle>
          </CardHeader>
          <CardContent>
            {results.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No results yet</p>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {results.map((result, index) => (
                  <div
                    key={result.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedResult(result)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <p className="font-semibold">Query {index + 1}</p>
                      {result.hallucination_score && result.hallucination_score > 0.5 && (
                        <Badge variant="destructive">
                          <AlertTriangle className="h-3 w-3 mr-1" />
                          Hallucination
                        </Badge>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-4 gap-2 text-sm">
                      <div>
                        <span className="text-gray-500">Recall@5:</span>
                        <span className="ml-1 font-semibold">
                          {result.recall_at_k?.[5] ? (result.recall_at_k[5] * 100).toFixed(0) : 'N/A'}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Faithfulness:</span>
                        <span className="ml-1 font-semibold">
                          {result.faithfulness ? (result.faithfulness * 100).toFixed(0) : 'N/A'}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Relevance:</span>
                        <span className="ml-1 font-semibold">
                          {result.answer_relevance ? (result.answer_relevance * 100).toFixed(0) : 'N/A'}%
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Hallucination:</span>
                        <span className="ml-1 font-semibold text-red-600">
                          {result.hallucination_score ? (result.hallucination_score * 100).toFixed(0) : 'N/A'}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Detail Modal */}
        {selectedResult && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle>Query Details</CardTitle>
                  <Button variant="outline" onClick={() => setSelectedResult(null)}>
                    Close
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="font-semibold text-sm text-gray-500 mb-1">Generated Answer</p>
                  <p className="bg-gray-50 p-3 rounded">{selectedResult.generated_answer}</p>
                </div>

                {selectedResult.hallucinated_spans && selectedResult.hallucinated_spans.length > 0 && (
                  <div>
                    <p className="font-semibold text-sm text-red-600 mb-2">
                      <AlertTriangle className="h-4 w-4 inline mr-1" />
                      Hallucinated Claims
                    </p>
                    <div className="space-y-2">
                      {selectedResult.hallucinated_spans.map((span, i) => (
                        <p key={i} className="bg-red-50 border-l-4 border-red-600 p-2 text-sm">
                          {span}
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Faithfulness</p>
                    <p className="text-xl font-bold">
                      {selectedResult.faithfulness ? (selectedResult.faithfulness * 100).toFixed(1) : 'N/A'}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Answer Relevance</p>
                    <p className="text-xl font-bold">
                      {selectedResult.answer_relevance ? (selectedResult.answer_relevance * 100).toFixed(1) : 'N/A'}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Citation Coverage</p>
                    <p className="text-xl font-bold">
                      {selectedResult.citation_coverage ? (selectedResult.citation_coverage * 100).toFixed(1) : 'N/A'}%
                    </p>
                  </div>
                </div>

                {selectedResult.retrieved_docs && (
                  <div>
                    <p className="font-semibold text-sm text-gray-500 mb-2">Retrieved Documents</p>
                    <div className="space-y-2">
                      {selectedResult.retrieved_docs.slice(0, 3).map((doc: any, i: number) => (
                        <div key={i} className="bg-gray-50 p-3 rounded text-sm">
                          <p className="font-semibold mb-1">Doc {i + 1}</p>
                          <p className="text-gray-600">
                            {typeof doc === 'string' ? doc : doc.text || doc.content || JSON.stringify(doc).substring(0, 200)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

