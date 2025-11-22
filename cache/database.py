"""SQLite database module for storing sessions and travel plans."""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path


class TravelPlannerDB:
    """Database manager for travel planner sessions and plans."""
    
    def __init__(self, db_path: str = "./cache/travel_planner.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Travel plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS travel_plans (
                plan_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                destination TEXT,
                start_date TEXT,
                end_date TEXT,
                plan_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, metadata: Optional[Dict] = None) -> bool:
        """Create a new session.
        
        Args:
            session_id: Unique session identifier
            metadata: Optional metadata dictionary
            
        Returns:
            True if session created successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO sessions (session_id, metadata)
                VALUES (?, ?)
            """, (session_id, json.dumps(metadata or {})))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Session already exists
            return False
        finally:
            conn.close()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "session_id": row["session_id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            }
        return None
    
    def update_session(self, session_id: str, metadata: Optional[Dict] = None):
        """Update session metadata.
        
        Args:
            session_id: Session identifier
            metadata: Metadata dictionary to update
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if metadata:
            cursor.execute("""
                UPDATE sessions 
                SET metadata = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (json.dumps(metadata), session_id))
        else:
            cursor.execute("""
                UPDATE sessions 
                SET updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
            """, (session_id,))
        
        conn.commit()
        conn.close()
    
    def save_travel_plan(self, plan_id: str, session_id: str, destination: str,
                        start_date: str, end_date: str, plan_data: Dict) -> bool:
        """Save or update a travel plan.
        
        Args:
            plan_id: Unique plan identifier
            session_id: Associated session ID
            destination: Travel destination
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            plan_data: Plan data dictionary
            
        Returns:
            True if saved successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO travel_plans 
                (plan_id, session_id, destination, start_date, end_date, plan_data)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(plan_id) DO UPDATE SET
                    session_id = excluded.session_id,
                    destination = excluded.destination,
                    start_date = excluded.start_date,
                    end_date = excluded.end_date,
                    plan_data = excluded.plan_data,
                    updated_at = CURRENT_TIMESTAMP
            """, (plan_id, session_id, destination, start_date, end_date, 
                  json.dumps(plan_data)))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving travel plan: {e}")
            return False
        finally:
            conn.close()
    
    def get_travel_plan(self, plan_id: str) -> Optional[Dict]:
        """Get a travel plan by ID.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Plan data dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM travel_plans WHERE plan_id = ?", (plan_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "plan_id": row["plan_id"],
                "session_id": row["session_id"],
                "destination": row["destination"],
                "start_date": row["start_date"],
                "end_date": row["end_date"],
                "plan_data": json.loads(row["plan_data"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        return None
    
    def get_session_plans(self, session_id: str) -> List[Dict]:
        """Get all travel plans for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of plan dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM travel_plans 
            WHERE session_id = ? 
            ORDER BY created_at DESC
        """, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "plan_id": row["plan_id"],
            "session_id": row["session_id"],
            "destination": row["destination"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "plan_data": json.loads(row["plan_data"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        } for row in rows]
    
    def add_chat_message(self, session_id: str, role: str, message: str):
        """Add a chat message to history.
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant)
            message: Message content
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (session_id, role, message)
            VALUES (?, ?, ?)
        """, (session_id, role, message))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, message, timestamp 
            FROM chat_history 
            WHERE session_id = ? 
            ORDER BY timestamp ASC 
            LIMIT ?
        """, (session_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "role": row["role"],
            "message": row["message"],
            "timestamp": row["timestamp"]
        } for row in rows]


