"""
Main pipeline script to orchestrate extraction and loading.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract.extract_reddit import extract_reddit_data, save_to_json
from load.load_reddit import insert_posts, get_total_posts

def run_pipeline(subreddit="dataengineering", limit=100, sort="new"):
    """
    Run full ETL pipeline: extract Reddit data and load to PostgreSQL.
    
    Args:
        subreddit: Subreddit to fetch from
        limit: Number of posts to fetch
        sort: Reddit listing type to fetch
    """
    print("=" * 60)
    print("Reddit Data Pipeline - Extract & Load")
    print("=" * 60)
    
    # Extract
    print(f"\n[EXTRACT] Fetching {limit} {sort} posts from r/{subreddit}...")
    posts = extract_reddit_data(subreddit=subreddit, limit=limit, sort=sort)
    
    if not posts:
        print("[ERROR] Extraction failed")
        return
    
    # Save to JSON
    json_file = save_to_json(posts)
    print(f"[OK] Extracted {len(posts)} posts")
    print(f"[OK] Saved to: {json_file}")
    
    # Load to Database
    print(f"\n[LOAD] Loading posts into PostgreSQL...")
    insert_posts(posts)
    
    # Summary
    total = get_total_posts()
    print(f"\n[SUMMARY] Database Statistics:")
    print(f"   Total posts in database: {total}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    run_pipeline(subreddit="dataengineering", limit=100, sort="new")
