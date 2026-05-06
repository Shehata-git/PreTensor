import os
import pytest
from memory_engine.db.sqlite_client import SQLiteClient
from memory_engine.db.qdrant_client import QdrantDBClient

def test_sqlite_client(tmp_path):
    # Use a temporary file instead of :memory: to maintain state between connections
    db_file = tmp_path / "test_memory.db"
    db = SQLiteClient(str(db_file))
    
    # Test session creation
    sid = db.create_session("Test Chat")
    assert sid is not None
    
    sessions = db.get_sessions()
    assert len(sessions) == 1
    assert sessions[0]["chat_title"] == "Test Chat"
    
    # Test message insertion
    db.add_message(sid, "user", "Hello world")
    db.add_message(sid, "assistant", "Hi there")
    
    msgs = db.get_messages(sid)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "Hello world"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"] == "Hi there"
    
    # Test limit
    db.add_message(sid, "user", "Third message")
    msgs = db.get_messages(sid, limit=2)
    assert len(msgs) == 2
    assert msgs[0]["content"] == "Hi there"
    assert msgs[1]["content"] == "Third message"


def test_qdrant_client():
    # Qdrant :memory: works fine as the client object holds the state
    client = QdrantDBClient(path=":memory:", vector_size=4)
    
    client.upsert_chunk("session_1", "test content 1", [1.0, 0.0, 0.0, 0.0])
    client.upsert_chunk("session_1", "test content 2", [0.0, 1.0, 0.0, 0.0])
    client.upsert_chunk("session_2", "test content 3", [0.0, 0.0, 1.0, 0.0])
    
    # Search closest to vector 1
    res = client.search_chunks([1.0, 0.0, 0.0, 0.0], limit=1)
    assert len(res) == 1
    assert res[0]["content"] == "test content 1"
    
    # Test session filter
    res = client.search_chunks([1.0, 0.0, 0.0, 0.0], limit=5, session_id="session_2")
    assert len(res) == 1
    assert res[0]["content"] == "test content 3"
