"""
RAG Pipeline Interface

Provides interface for calling RAG systems (API or local).
"""
from typing import List, Dict, Any, Optional
import httpx
from ..core.logging import log


class RAGPipeline:
    """Base interface for RAG pipelines"""
    
    async def query(self, query_text: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query the RAG pipeline.
        
        Args:
            query_text: The user query
            config: Optional configuration
            
        Returns:
            Dict with 'retrieved_docs' and 'generated_answer'
        """
        raise NotImplementedError


class APIRAGPipeline(RAGPipeline):
    """RAG Pipeline that calls an external API"""
    
    def __init__(self, endpoint: str):
        """
        Initialize API-based RAG pipeline.
        
        Args:
            endpoint: API endpoint URL
        """
        self.endpoint = endpoint
        
    async def query(self, query_text: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query RAG API endpoint.
        
        Expected API response format:
        {
            "retrieved_docs": [...],
            "generated_answer": "...",
            "metadata": {...}  # optional
        }
        """
        config = config or {}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "query": query_text,
                    **config
                }
                
                log.debug(f"Calling RAG API: {self.endpoint}")
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                
                data = response.json()
                
                # Validate response
                if "retrieved_docs" not in data or "generated_answer" not in data:
                    raise ValueError("Invalid API response format. Expected 'retrieved_docs' and 'generated_answer'")
                
                return {
                    "retrieved_docs": data["retrieved_docs"],
                    "generated_answer": data["generated_answer"],
                    "metadata": data.get("metadata", {})
                }
                
        except httpx.HTTPError as e:
            log.error(f"HTTP error calling RAG API: {e}")
            raise
        except Exception as e:
            log.error(f"Error querying RAG pipeline: {e}")
            raise


class MockRAGPipeline(RAGPipeline):
    """Mock RAG Pipeline for testing"""
    
    def __init__(self):
        """Initialize mock pipeline"""
        pass
    
    async def query(self, query_text: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Return mock response.
        Useful for testing the evaluation system without a real RAG.
        """
        return {
            "retrieved_docs": [
                {"id": "doc1", "text": "This is a sample document about the query topic."},
                {"id": "doc2", "text": "Another relevant document with more information."},
                {"id": "doc3", "text": "A third document providing additional context."}
            ],
            "generated_answer": f"Based on the retrieved documents, here is an answer to: {query_text}. The information suggests various relevant points."
        }


def create_rag_pipeline(endpoint: Optional[str] = None, pipeline_type: str = "api") -> RAGPipeline:
    """
    Factory function to create RAG pipeline instances.
    
    Args:
        endpoint: API endpoint (required for 'api' type)
        pipeline_type: Type of pipeline ('api' or 'mock')
        
    Returns:
        RAGPipeline instance
    """
    if pipeline_type == "mock":
        return MockRAGPipeline()
    elif pipeline_type == "api":
        if not endpoint:
            raise ValueError("Endpoint required for API pipeline")
        return APIRAGPipeline(endpoint)
    else:
        raise ValueError(f"Unknown pipeline type: {pipeline_type}")

