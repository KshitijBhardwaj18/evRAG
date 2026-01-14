"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { versionApi, type DatasetVersion } from "@/lib/api"
import { Clock, RotateCcw } from "lucide-react"

interface VersionHistoryProps {
  datasetId: string
}

export default function VersionHistory({ datasetId }: VersionHistoryProps) {
  const [versions, setVersions] = useState<DatasetVersion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadVersions()
  }, [datasetId])

  const loadVersions = async () => {
    try {
      const response = await versionApi.list(datasetId)
      setVersions(response.data)
    } catch (error) {
      console.error("Failed to load versions:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleRollback = async (versionNumber: number) => {
    if (!confirm(`Roll back to version ${versionNumber}? This will create a new version.`)) {
      return
    }

    try {
      await versionApi.rollback(datasetId, versionNumber)
      await loadVersions()
      window.location.reload()
    } catch (error) {
      console.error("Failed to rollback:", error)
      alert("Failed to rollback version")
    }
  }

  if (loading) {
    return <p className="text-gray-500">Loading versions...</p>
  }

  if (versions.length === 0) {
    return <p className="text-gray-500">No version history</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Version History</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {versions.map((version) => (
            <div
              key={version.id}
              className="border rounded-lg p-4 hover:bg-gray-50 transition"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={version.version_number === versions[0].version_number ? "default" : "secondary"}>
                      v{version.version_number}
                    </Badge>
                    {version.version_number === versions[0].version_number && (
                      <span className="text-xs text-green-600 font-semibold">Current</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {version.changes_summary || "No description"}
                  </p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(version.created_at).toLocaleString()}
                    </div>
                    <span>{version.item_count} items</span>
                  </div>
                </div>
                {version.version_number !== versions[0].version_number && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleRollback(version.version_number)}
                  >
                    <RotateCcw className="h-3 w-3 mr-1" />
                    Rollback
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

