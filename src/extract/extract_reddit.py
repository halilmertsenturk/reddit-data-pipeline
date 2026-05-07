import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def extract_reddit_data(subreddit="dataengineering", limit=10):
    """
    Fetch hot posts from a Reddit subreddit using public JSON endpoint.
    
    Args:
        subreddit: Subreddit name (default: dataengineering)
        limit: Number of posts to fetch (default: 10)
    
    Returns:
        List of post dictionaries
    """
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    headers = {
        "User-Agent": "Reddit Data Pipeline (Python requests)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        posts = []
        for item in data["data"]["children"]:
            post = item["data"]
            posts.append({
                "post_id": post.get("id"),
                "subreddit": post.get("subreddit"),
                "title": post.get("title"),
                "author": post.get("author"),
                "score": post.get("score"),
                "num_comments": post.get("num_comments"),
                "created_utc": post.get("created_utc"),
                "url": post.get("url")
            })
        
        return posts
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch Reddit data: {e}")
        return []

def save_to_json(posts, output_dir="data/raw"):
    """
    Save extracted posts to JSON file with timestamp.
    
    Args:
        posts: List of post dictionaries
        output_dir: Directory to save JSON file
    
    Returns:
        Path to saved file
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/reddit_posts_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(posts, f, indent=2)
    
    return filename

if __name__ == "__main__":
    print("[EXTRACT] Fetching Reddit data...")
    posts = extract_reddit_data(subreddit="dataengineering", limit=10)
    
    if posts:
        filename = save_to_json(posts)
        print(f"[OK] Extracted {len(posts)} posts")
        print(f"[OK] Saved to: {filename}")
        print("\n[SAMPLE] First post:")
        print(json.dumps(posts[0], indent=2))
    else:
        print("[ERROR] Failed to extract posts")
