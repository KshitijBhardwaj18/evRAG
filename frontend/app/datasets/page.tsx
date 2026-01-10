"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { datasetApi, type Dataset } from "@/lib/api"
import { Upload, FileText, Calendar, ArrowLeft } from "lucide-react"

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    loadDatasets()
  }, [])

  const loadDatasets = async () => {
    try {
      const response = await datasetApi.list()
      setDatasets(response.data)
    } catch (error) {
      console.error("Failed to load datasets:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      await datasetApi.upload(file)
      await loadDatasets()
      event.target.value = "" // Reset input
    } catch (error) {
      console.error("Failed to upload dataset:", error)
      alert("Failed to upload dataset. Please check the format.")
    } finally {
      setUploading(false)
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
          <h1 className="text-2xl font-bold">Datasets</h1>
          <div className="w-24" /> {/* Spacer for centering */}
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Upload Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Upload Dataset</CardTitle>
            <CardDescription>
              Upload a CSV, JSON, or JSONL file with queries and ground truth
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <label className="cursor-pointer">
                <input
                  type="file"
                  className="hidden"
                  accept=".csv,.json,.jsonl"
                  onChange={handleFileUpload}
                  disabled={uploading}
                />
                <Button disabled={uploading} asChild>
                  <span>
                    <Upload className="h-4 w-4 mr-2" />
                    {uploading ? "Uploading..." : "Choose File"}
                  </span>
                </Button>
              </label>
              <p className="text-sm text-gray-500">
                Supported formats: CSV, JSON, JSONL
              </p>
            </div>
            
            <div className="mt-4 p-4 bg-gray-50 rounded-md">
              <p className="text-sm font-semibold mb-2">Expected format:</p>
              <pre className="text-xs bg-white p-2 rounded overflow-x-auto">
{`{
  "items": [
    {
      "query": "What is RAG?",
      "ground_truth_docs": ["doc1", "doc2"],
      "ground_truth_answer": "RAG is..."
    }
  ]
}`}
              </pre>
            </div>
          </CardContent>
        </Card>

        {/* Datasets List */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Your Datasets</h2>
          
          {loading ? (
            <p className="text-gray-500">Loading datasets...</p>
          ) : datasets.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-gray-500">
                No datasets yet. Upload your first dataset to get started.
              </CardContent>
            </Card>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {datasets.map((dataset) => (
                <Link key={dataset.id} href={`/datasets/${dataset.id}`}>
                  <Card className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <FileText className="h-6 w-6 text-blue-600" />
                        <Badge variant="secondary">{dataset.file_format || 'json'}</Badge>
                      </div>
                      <CardTitle className="text-lg mt-2">{dataset.name}</CardTitle>
                      {dataset.description && (
                        <CardDescription>{dataset.description}</CardDescription>
                      )}
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Items:</span>
                          <span className="font-semibold">{dataset.total_items}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-500">
                          <Calendar className="h-3 w-3" />
                          <span className="text-xs">
                            {new Date(dataset.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

