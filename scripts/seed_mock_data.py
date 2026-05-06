import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory_engine.db.sqlite_client import SQLiteClient

def seed_data(db_path: str = "memory.db"):
    db = SQLiteClient(db_path)
    
    # Session 1: Project Planning
    sid1 = db.create_session("Project Alpha Planning")
    db.add_message(sid1, "user", "I need to start planning Project Alpha. It's a new web app.")
    db.add_message(sid1, "assistant", "Great! What is the core functionality of Project Alpha?")
    db.add_message(sid1, "user", "It's a task manager for developers.")
    db.add_message(sid1, "assistant", "Understood. A developer-focused task manager. Should we outline the tech stack?")
    db.add_message(sid1, "user", "Yes, let's use Python on the backend and React on the frontend.")
    
    # Session 2: Daily standup notes
    sid2 = db.create_session("Daily Standup")
    db.add_message(sid2, "user", "Remind me to tell the team I fixed the auth bug.")
    db.add_message(sid2, "assistant", "I've noted that. You fixed the auth bug.")
    db.add_message(sid2, "user", "Also, mention we need to review the Q3 roadmap.")
    db.add_message(sid2, "assistant", "Noted. I will remind you to mention the Q3 roadmap review.")
    
    print("Database seeded successfully with mock data.")

if __name__ == "__main__":
    seed_data()
