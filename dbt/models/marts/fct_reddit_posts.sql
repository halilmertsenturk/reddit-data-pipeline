{{ config(materialized='table') }}

SELECT
    post_id,
    subreddit,
    title,
    author,
    score,
    num_comments,
    created_utc,
    url,
    loaded_at,
    CASE 
        WHEN score > 100 THEN 'viral'
        WHEN score > 50 THEN 'popular'
        WHEN score > 10 THEN 'trending'
        ELSE 'normal'
    END AS engagement_level,
    ROW_NUMBER() OVER (PARTITION BY subreddit ORDER BY score DESC) AS rank_in_subreddit
FROM {{ ref('stg_reddit_posts') }}
