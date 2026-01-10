"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { evaluationApi, type EvaluationRun } from "@/lib/api"
import { ArrowLeft, Clock, CheckCircle, XCircle, Loader } from "lucide-react"

export default function RunsPage() {
  const [runs, setRuns] = useState<EvaluationRun[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRuns()
    const interval = setInterval(loadRuns, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const loadRuns = async () => {
    try {
      const response = await evaluationApi.list()
      setRuns(response.data)
    } catch (error) {
      console.error("Failed to load runs:", error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-600"><CheckCircle className="h-3 w-3 mr-1" />Completed</Badge>
      case "running":
        return <Badge className="bg-blue-600"><Loader className="h-3 w-3 mr-1 animate-spin" />Running</Badge>
      case "failed":
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />Failed</Badge>
      default:
        return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1" />Pending</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="border-b bg-white">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Link>
          <h1 className="text-2xl font-bold">Evaluation Runs</h1>
          <div className="w-24" />
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <p className="text-gray-500">Loading runs...</p>
        ) : runs.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center text-gray-500">
              No evaluation runs yet. Create a dataset and start an evaluation.
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {runs.map((run) => (
              <Link key={run.id} href={`/runs/${run.id}`}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-xl mb-2">{run.name}</CardTitle>
                        {run.description && (
                          <p className="text-sm text-gray-600">{run.description}</p>
                        )}
                      </div>
                      {getStatusBadge(run.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Progress</p>
                        <p className="text-lg font-semibold">
                          {run.completed_items} / {run.total_items}
                        </p>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{
                              width: `${(run.completed_items / run.total_items) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                      
                      {run.metrics && (
                        <>
                          <div>
                            <p className="text-sm text-gray-500">Avg Recall@5</p>
                            <p className="text-lg font-semibold">
                              {(run.metrics.avg_recall_at_5 * 100).toFixed(1)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500">Avg Faithfulness</p>
                            <p className="text-lg font-semibold">
                              {(run.metrics.avg_faithfulness * 100).toFixed(1)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500">Hallucination Rate</p>
                            <p className="text-lg font-semibold text-red-600">
                              {(run.metrics.hallucination_rate * 100).toFixed(1)}%
                            </p>
                          </div>
                        </>
                      )}
                    </div>
                    
                    <div className="mt-4 text-sm text-gray-500">
                      Created: {new Date(run.created_at).toLocaleString()}
                      {run.completed_at && (
                        <> • Completed: {new Date(run.completed_at).toLocaleString()}</>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

