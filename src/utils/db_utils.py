"""
Database utility functions for Reddit Data Pipeline.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    """Create and return database connection."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def execute_query(query, fetch=False):
    """Execute a SQL query."""
    conn = connect_db()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        cur.execute(query)
        
        if fetch:
            result = cur.fetchall()
        else:
            conn.commit()
            result = None
        
        return result
    
    finally:
        cur.close()
        conn.close()
