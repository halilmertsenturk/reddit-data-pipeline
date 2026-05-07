CREATE TABLE IF NOT EXISTS reddit_posts (
    post_id TEXT PRIMARY KEY,
    subreddit TEXT,
    title TEXT,
    author TEXT,
    score INT,
    num_comments INT,
    created_utc BIGINT,
    url TEXT
);
