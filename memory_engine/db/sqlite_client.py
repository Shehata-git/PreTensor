import sqlite3
from typing import List, Dict, Any, Optional
import datetime
import uuid

class SQLiteClient:
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    chat_title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            ''')
            conn.commit()

    def create_session(self, chat_title: str) -> str:
        session_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (session_id, chat_title) VALUES (?, ?)",
                (session_id, chat_title)
            )
            conn.commit()
        return session_id

    def add_message(self, session_id: str, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC"
        params = [session_id]
        
        if limit is not None:
            query = "SELECT role, content, timestamp FROM (SELECT * FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id ASC"
            params = [session_id, limit]
            
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [{"role": row["role"], "content": row["content"], "timestamp": row["timestamp"]} for row in rows]
            
    def get_sessions(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT session_id, chat_title, created_at FROM sessions ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [{"session_id": row["session_id"], "chat_title": row["chat_title"], "created_at": row["created_at"]} for row in rows]
