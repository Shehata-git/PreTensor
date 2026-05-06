from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
import uuid

class QdrantDBClient:
    def __init__(self, path: str = "qdrant_db", collection_name: str = "memory_chunks", vector_size: int = 768):
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # In-memory for tests if path is ":memory:"
        if path == ":memory:":
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(path=path)
            
        self._init_collection()

    def _init_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def upsert_chunk(self, session_id: str, content: str, vector: List[float]):
        point_id = str(uuid.uuid4())
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "session_id": session_id,
                        "content": content
                    }
                )
            ]
        )

    def search_chunks(self, vector: List[float], limit: int = 5, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query_filter = None
        if session_id:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="session_id",
                        match=MatchValue(value=session_id)
                    )
                ]
            )
            
        # Use query_points for the modern Qdrant API
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            query_filter=query_filter,
            limit=limit
        )
        
        # Extract points from the QueryResponse
        return [
            {
                "content": point.payload["content"], 
                "session_id": point.payload["session_id"], 
                "score": point.score
            } 
            for point in search_result.points
        ]
