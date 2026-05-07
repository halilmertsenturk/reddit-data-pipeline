import json
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    """Connect to PostgreSQL database."""
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
        print(f"[ERROR] Database connection failed: {e}")
        return None

def load_json_file(filepath):
    """Load JSON file containing Reddit posts."""
    with open(filepath, "r") as f:
        return json.load(f)

def insert_posts(posts):
    """
    Insert posts into reddit_posts table.
    Handles duplicates by ignoring posts with existing post_id.
    
    Args:
        posts: List of post dictionaries
    
    Returns:
        Number of rows inserted
    """
    conn = connect_db()
    if not conn:
        return 0
    
    try:
        cur = conn.cursor()
        
        # Prepare data for insertion
        data = [
            (
                post.get("post_id"),
                post.get("subreddit"),
                post.get("title"),
                post.get("author"),
                post.get("score"),
                post.get("num_comments"),
                post.get("created_utc"),
                post.get("url")
            )
            for post in posts
        ]
        
        # Insert with ON CONFLICT DO NOTHING to handle duplicates
        query = """
        INSERT INTO reddit_posts 
        (post_id, subreddit, title, author, score, num_comments, created_utc, url)
        VALUES %s
        ON CONFLICT (post_id) DO NOTHING
        """
        
        execute_values(cur, query, data)
        rows_inserted = cur.rowcount
        conn.commit()
        
        print(f"[OK] Inserted {rows_inserted} new posts into database")
        
        return rows_inserted
    
    except Exception as e:
        print(f"[ERROR] Failed to insert posts: {e}")
        conn.rollback()
        return 0
    
    finally:
        cur.close()
        conn.close()

def get_total_posts():
    """Get total number of posts in database."""
    conn = connect_db()
    if not conn:
        return 0
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM reddit_posts")
        count = cur.fetchone()[0]
        return count
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        print(f"[LOAD] Loading posts from: {filepath}")
        posts = load_json_file(filepath)
        insert_posts(posts)
        total = get_total_posts()
        print(f"[OK] Total posts in database: {total}")
    else:
        print("Usage: python load_reddit.py <json_filepath>")
