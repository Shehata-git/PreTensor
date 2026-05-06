from memory_engine.nlp.cleaner import NLPCleaner
from memory_engine.embedding.onnx_embedder import ONNXEmbedder
from memory_engine.db.qdrant_client import QdrantDBClient
from typing import List

class SemanticPipeline:
    def __init__(self, qdrant_path: str = "qdrant_db"):
        self.cleaner = NLPCleaner()
        self.embedder = ONNXEmbedder()
        self.qdrant = QdrantDBClient(path=qdrant_path)

    def process_and_store(self, session_id: str, content: str):
        """
        Cleans the content, embeds it, and stores it in Qdrant.
        """
        # 1. Clean the text to semantic minima
        cleaned_text = self.cleaner.clean_text(content)
        
        # Skip if cleaning resulted in empty string
        if not cleaned_text.strip():
            return
            
        # 2. Generate embedding
        vector = self.embedder.embed(cleaned_text)
        
        # 3. Upsert to Qdrant
        self.qdrant.upsert_chunk(
            session_id=session_id,
            content=content, # Store original content for retrieval
            vector=vector
        )

    def retrieve_relevant(self, query: str, limit: int = 5, session_id: str = None) -> List[str]:
        """
        Retrieves relevant chunks based on a query.
        """
        # Clean query for better matching? 
        # Usually we embed the raw query (with 'search_query: ' prefix)
        # We'll use a specific query prefix in the embedder if we wanted to be strict,
        # but for simplicity we'll use the embedder's default.
        
        # Note: In a real app, we'd distinguish 'search_query' from 'search_document'
        # For now, let's just embed the query text.
        query_vector = self.embedder.embed(query)
        
        results = self.qdrant.search_chunks(
            vector=query_vector,
            limit=limit,
            session_id=session_id
        )
        
        return [res["content"] for res in results]
