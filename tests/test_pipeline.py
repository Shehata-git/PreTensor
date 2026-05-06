import pytest
from memory_engine.nlp.cleaner import NLPCleaner
from memory_engine.pipeline import SemanticPipeline
from unittest.mock import MagicMock, patch

def test_nlp_cleaner():
    cleaner = NLPCleaner()
    raw_text = "I am *planning* a [new project](https://example.com) for `NLP`. It's great!"
    cleaned = cleaner.clean_text(raw_text)
    
    # Check that markdown fluff is gone
    assert "project" in cleaned
    assert "plan" in cleaned # planning -> plan
    assert "https://example.com" not in cleaned
    
def test_pipeline_flow():
    # Patch ONNXEmbedder so it doesn't initialize or download anything
    with patch("memory_engine.pipeline.ONNXEmbedder") as MockEmbedder:
        mock_embedder_instance = MockEmbedder.return_value
        mock_embedder_instance.embed.return_value = [0.1] * 768
        
        # Patch NLPCleaner if we want to isolate further, but it's lightweight enough
        pipeline = SemanticPipeline(qdrant_path=":memory:")
        
        pipeline.process_and_store("sid_123", "Helpful message about tasks.")
        
        # Verify upsert was called (indirectly by searching)
        results = pipeline.retrieve_relevant("task")
        assert len(results) == 1
        assert "Helpful message about tasks." in results
