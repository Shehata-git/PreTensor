import pytest
from unittest.mock import MagicMock, patch
from memory_engine.llm.orchestrator import LLMOrchestrator

@pytest.fixture
def orchestrator(tmp_path):
    db_path = tmp_path / "test_memory.db"
    # Patch ONNXEmbedder and Qdrant to avoid real init
    with patch("memory_engine.pipeline.ONNXEmbedder"), \
         patch("memory_engine.pipeline.QdrantDBClient"):
        orch = LLMOrchestrator(db_path=str(db_path))
        return orch

def test_method_a_context_construction(orchestrator):
    sid = orchestrator.sqlite.create_session("Test")
    orchestrator.sqlite.add_message(sid, "user", "Message 1")
    
    with patch.object(orchestrator, "_call_ollama", return_value="Mocked") as mock_call:
        res = orchestrator.generate_method_a(sid, "Current Prompt")
        
        assert res == "Mocked"
        args, _ = mock_call.call_args
        prompt = args[0]
        assert "Message 1" in prompt
        assert "Current Prompt" in prompt

def test_method_b_context_construction(orchestrator):
    sid = orchestrator.sqlite.create_session("Test")
    
    with patch.object(orchestrator.pipeline, "retrieve_relevant", return_value=["Chunk 1"]) as mock_retrieval, \
         patch.object(orchestrator, "_call_ollama", return_value="Mocked") as mock_call:
        
        res = orchestrator.generate_method_b(sid, "Current Prompt")
        
        assert res == "Mocked"
        mock_retrieval.assert_called_once()
        args, _ = mock_call.call_args
        prompt = args[0]
        assert "Chunk 1" in prompt
        assert "Current Prompt" in prompt
