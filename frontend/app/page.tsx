"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, BarChart3, AlertTriangle, Zap } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Navigation */}
      <nav className="border-b bg-white">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-8 w-8 text-blue-600" />
            <h1 className="text-2xl font-bold">EvRAG</h1>
          </div>
          <div className="flex gap-4">
            <Link href="/datasets">
              <Button variant="outline">Datasets</Button>
            </Link>
            <Link href="/runs">
              <Button>Evaluation Runs</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4">
            Production-Grade RAG Evaluation
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Comprehensive metrics for retrieval quality, generation accuracy, and hallucination detection
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/datasets">
              <Button size="lg">Upload Dataset</Button>
            </Link>
            <Link href="/runs">
              <Button size="lg" variant="outline">View Runs</Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <Card>
            <CardHeader>
              <CheckCircle className="h-8 w-8 text-green-600 mb-2" />
              <CardTitle className="text-lg">Retrieval Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Recall@K</li>
                <li>• Precision@K</li>
                <li>• MRR & MAP</li>
                <li>• Hit Rate & Coverage</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Zap className="h-8 w-8 text-blue-600 mb-2" />
              <CardTitle className="text-lg">Generation Quality</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Faithfulness</li>
                <li>• Answer Relevance</li>
                <li>• Context Utilization</li>
                <li>• ROUGE-L & F1</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <AlertTriangle className="h-8 w-8 text-red-600 mb-2" />
              <CardTitle className="text-lg">Hallucination Detection</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• LLM-as-Judge</li>
                <li>• Citation Check</li>
                <li>• Embedding Drift</li>
                <li>• Aggregated Score</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <BarChart3 className="h-8 w-8 text-purple-600 mb-2" />
              <CardTitle className="text-lg">Observability</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Real-time tracking</li>
                <li>• Per-query breakdown</li>
                <li>• Run comparison</li>
                <li>• Trend analysis</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Quick Start */}
        <Card className="max-w-3xl mx-auto">
          <CardHeader>
            <CardTitle>Quick Start</CardTitle>
            <CardDescription>Get started with RAG evaluation in 3 steps</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                  1
                </div>
                <div>
                  <h3 className="font-semibold mb-1">Upload Dataset</h3>
                  <p className="text-sm text-gray-600">
                    Upload your evaluation dataset (CSV, JSON, or JSONL) with queries and ground truth
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                  2
                </div>
                <div>
                  <h3 className="font-semibold mb-1">Connect RAG Pipeline</h3>
                  <p className="text-sm text-gray-600">
                    Provide your RAG API endpoint or use the mock pipeline for testing
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-4">
                <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                  3
                </div>
                <div>
                  <h3 className="font-semibold mb-1">View Results</h3>
                  <p className="text-sm text-gray-600">
                    Analyze comprehensive metrics, identify issues, and compare runs over time
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

