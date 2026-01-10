"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { datasetApi, evaluationApi, type Dataset, type DatasetItem } from "@/lib/api"
import { ArrowLeft, Play } from "lucide-react"

export default function DatasetDetailPage() {
  const params = useParams()
  const router = useRouter()
  const datasetId = params.id as string
  
  const [dataset, setDataset] = useState<Dataset & { items: DatasetItem[] } | null>(null)
  const [loading, setLoading] = useState(true)
  const [showCreateRun, setShowCreateRun] = useState(false)
  const [runName, setRunName] = useState("")
  const [ragEndpoint, setRagEndpoint] = useState("")
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadDataset()
  }, [datasetId])

  const loadDataset = async () => {
    try {
      const response = await datasetApi.get(datasetId)
      setDataset(response.data)
    } catch (error) {
      console.error("Failed to load dataset:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateRun = async () => {
    if (!runName.trim()) {
      alert("Please enter a run name")
      return
    }

    setCreating(true)
    try {
      const response = await evaluationApi.create({
        dataset_id: datasetId,
        name: runName,
        rag_endpoint: ragEndpoint || undefined,
      })
      
      router.push(`/runs/${response.data.id}`)
    } catch (error) {
      console.error("Failed to create run:", error)
      alert("Failed to create evaluation run")
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p>Loading dataset...</p>
      </div>
    )
  }

  if (!dataset) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p>Dataset not found</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="border-b bg-white">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/datasets" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-4 w-4" />
            Back to Datasets
          </Link>
          <h1 className="text-2xl font-bold">{dataset.name}</h1>
          <Button onClick={() => setShowCreateRun(true)}>
            <Play className="h-4 w-4 mr-2" />
            Start Evaluation
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Dataset Info */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Dataset Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500">Total Items</p>
                <p className="text-2xl font-bold">{dataset.total_items}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Format</p>
                <p className="text-lg font-semibold">{dataset.file_format || 'json'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Created</p>
                <p className="text-lg">{new Date(dataset.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            {dataset.description && (
              <p className="mt-4 text-gray-600">{dataset.description}</p>
            )}
          </CardContent>
        </Card>

        {/* Sample Items */}
        <Card>
          <CardHeader>
            <CardTitle>Sample Items</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dataset.items.slice(0, 5).map((item, index) => (
                <div key={item.id} className="border-l-4 border-blue-600 pl-4 py-2">
                  <p className="font-semibold text-sm text-gray-500 mb-1">Query {index + 1}</p>
                  <p className="mb-2">{item.query}</p>
                  {item.ground_truth_docs && (
                    <p className="text-sm text-gray-600">
                      Ground truth docs: {JSON.stringify(item.ground_truth_docs).substring(0, 100)}...
                    </p>
                  )}
                </div>
              ))}
              {dataset.items.length > 5 && (
                <p className="text-sm text-gray-500 text-center">
                  ...and {dataset.items.length - 5} more items
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Create Run Modal */}
        {showCreateRun && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Create Evaluation Run</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Run Name</label>
                    <input
                      type="text"
                      className="w-full mt-1 px-3 py-2 border rounded-md"
                      placeholder="e.g., Baseline Run"
                      value={runName}
                      onChange={(e) => setRunName(e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">RAG Endpoint (Optional)</label>
                    <input
                      type="text"
                      className="w-full mt-1 px-3 py-2 border rounded-md"
                      placeholder="http://localhost:5000/query"
                      value={ragEndpoint}
                      onChange={(e) => setRagEndpoint(e.target.value)}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Leave empty to use mock pipeline
                    </p>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      onClick={handleCreateRun}
                      disabled={creating}
                      className="flex-1"
                    >
                      {creating ? "Creating..." : "Create & Start"}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => setShowCreateRun(false)}
                      disabled={creating}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}

