"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { evaluationApi, type EvaluationRun } from "@/lib/api"
import { ArrowLeft, ArrowUp, ArrowDown, Minus } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function CompareRunsPage() {
  const searchParams = useSearchParams()
  const run1Id = searchParams.get('run1')
  const run2Id = searchParams.get('run2')
  
  const [run1, setRun1] = useState<EvaluationRun | null>(null)
  const [run2, setRun2] = useState<EvaluationRun | null>(null)
  const [comparison, setComparison] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (run1Id && run2Id) {
      loadComparison()
    }
  }, [run1Id, run2Id])

  const loadComparison = async () => {
    if (!run1Id || !run2Id) return

    try {
      const response = await evaluationApi.compare(run1Id, run2Id)
      setRun1(response.data.run1)
      setRun2(response.data.run2)
      setComparison(response.data)
    } catch (error) {
      console.error("Failed to load comparison:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p>Loading comparison...</p>
      </div>
    )
  }

  if (!run1 || !run2 || !comparison) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p>Failed to load comparison. Please select two runs.</p>
      </div>
    )
  }

  const getDeltaIcon = (delta: number) => {
    if (delta > 0.01) return <ArrowUp className="h-4 w-4 text-green-600" />
    if (delta < -0.01) return <ArrowDown className="h-4 w-4 text-red-600" />
    return <Minus className="h-4 w-4 text-gray-400" />
  }

  const getDeltaColor = (delta: number) => {
    if (delta > 0.01) return "text-green-600"
    if (delta < -0.01) return "text-red-600"
    return "text-gray-400"
  }

  // Prepare comparison chart data
  const comparisonData = [
    {
      metric: 'Recall@5',
      [run1.name]: (run1.metrics?.avg_recall_at_5 || 0) * 100,
      [run2.name]: (run2.metrics?.avg_recall_at_5 || 0) * 100,
    },
    {
      metric: 'Faithfulness',
      [run1.name]: (run1.metrics?.avg_faithfulness || 0) * 100,
      [run2.name]: (run2.metrics?.avg_faithfulness || 0) * 100,
    },
    {
      metric: 'Relevance',
      [run1.name]: (run1.metrics?.avg_answer_relevance || 0) * 100,
      [run2.name]: (run2.metrics?.avg_answer_relevance || 0) * 100,
    },
    {
      metric: 'MRR',
      [run1.name]: (run1.metrics?.avg_mrr || 0) * 100,
      [run2.name]: (run2.metrics?.avg_mrr || 0) * 100,
    },
  ]

  const metricsToCompare = [
    { key: 'avg_recall_at_5', label: 'Avg Recall@5', format: (v: number) => `${(v * 100).toFixed(1)}%` },
    { key: 'avg_precision_at_5', label: 'Avg Precision@5', format: (v: number) => `${(v * 100).toFixed(1)}%` },
    { key: 'avg_mrr', label: 'Avg MRR', format: (v: number) => v.toFixed(3) },
    { key: 'avg_map_score', label: 'Avg MAP', format: (v: number) => v.toFixed(3) },
    { key: 'avg_faithfulness', label: 'Avg Faithfulness', format: (v: number) => `${(v * 100).toFixed(1)}%` },
    { key: 'avg_answer_relevance', label: 'Avg Answer Relevance', format: (v: number) => `${(v * 100).toFixed(1)}%` },
    { key: 'avg_context_utilization', label: 'Avg Context Utilization', format: (v: number) => `${(v * 100).toFixed(1)}%` },
    { key: 'hallucination_rate', label: 'Hallucination Rate', format: (v: number) => `${(v * 100).toFixed(1)}%`, inverse: true },
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
          <h1 className="text-2xl font-bold">Compare Runs</h1>
          <div className="w-24" />
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Run Headers */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>{run1.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500">
                Created: {new Date(run1.created_at).toLocaleDateString()}
              </p>
              {run1.description && (
                <p className="text-sm mt-2">{run1.description}</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{run2.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500">
                Created: {new Date(run2.created_at).toLocaleDateString()}
              </p>
              {run2.description && (
                <p className="text-sm mt-2">{run2.description}</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Comparison Chart */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Metric Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" />
                <YAxis label={{ value: 'Score (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey={run1.name} fill="#3b82f6" />
                <Bar dataKey={run2.name} fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Detailed Metrics Table */}
        <Card>
          <CardHeader>
            <CardTitle>Detailed Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Metric</th>
                    <th className="text-right py-3 px-4">{run1.name}</th>
                    <th className="text-right py-3 px-4">{run2.name}</th>
                    <th className="text-right py-3 px-4">Delta</th>
                    <th className="text-right py-3 px-4">Change</th>
                  </tr>
                </thead>
                <tbody>
                  {metricsToCompare.map(({ key, label, format, inverse }) => {
                    const val1 = run1.metrics?.[key] || 0
                    const val2 = run2.metrics?.[key] || 0
                    const delta = comparison.metric_deltas?.[key] || 0
                    const improvement = comparison.improvement_pct?.[key] || 0
                    
                    // For inverse metrics (like hallucination), negative delta is good
                    const effectiveDelta = inverse ? -delta : delta
                    
                    return (
                      <tr key={key} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 font-medium">{label}</td>
                        <td className="py-3 px-4 text-right">{format(val1)}</td>
                        <td className="py-3 px-4 text-right">{format(val2)}</td>
                        <td className={`py-3 px-4 text-right font-semibold ${getDeltaColor(effectiveDelta)}`}>
                          <div className="flex items-center justify-end gap-1">
                            {getDeltaIcon(effectiveDelta)}
                            {format(Math.abs(delta))}
                          </div>
                        </td>
                        <td className={`py-3 px-4 text-right font-semibold ${getDeltaColor(effectiveDelta)}`}>
                          {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}%
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Summary */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm">
                <span className="font-semibold">{run2.name}</span> compared to{" "}
                <span className="font-semibold">{run1.name}</span>:
              </p>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                {comparison.metric_deltas?.avg_recall_at_5 > 0 && (
                  <li className="text-green-600">
                    Improved recall by {(comparison.improvement_pct?.avg_recall_at_5 || 0).toFixed(1)}%
                  </li>
                )}
                {comparison.metric_deltas?.avg_faithfulness > 0 && (
                  <li className="text-green-600">
                    Improved faithfulness by {(comparison.improvement_pct?.avg_faithfulness || 0).toFixed(1)}%
                  </li>
                )}
                {comparison.metric_deltas?.hallucination_rate < 0 && (
                  <li className="text-green-600">
                    Reduced hallucination rate by {Math.abs(comparison.improvement_pct?.hallucination_rate || 0).toFixed(1)}%
                  </li>
                )}
                {comparison.metric_deltas?.avg_recall_at_5 < 0 && (
                  <li className="text-red-600">
                    Decreased recall by {Math.abs(comparison.improvement_pct?.avg_recall_at_5 || 0).toFixed(1)}%
                  </li>
                )}
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

