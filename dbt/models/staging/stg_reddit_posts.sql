{{ config(materialized='view') }}

SELECT
    post_id,
    subreddit,
    title,
    author,
    score,
    num_comments,
    created_utc,
    url,
    CURRENT_TIMESTAMP AS loaded_at
FROM {{ source('reddit', 'reddit_posts') }}
