# Reddit Data Engineering Pipeline

A beginner-friendly data engineering project that extracts real-time data from Reddit and loads it into PostgreSQL.

## Features

- **Extract**: Fetch hot posts from Reddit using public JSON endpoints (no OAuth required)
- **Load**: Insert data into PostgreSQL with duplicate handling
- **Docker**: Fully containerized with docker-compose for easy setup
- **Production-Ready**: Proper error handling, logging, and database transactions

## Architecture

```
┌─────────────────────────────────────────────┐
│  Reddit Public JSON API                     │
│  (https://reddit.com/r/*/hot.json)          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Extract (Python + requests)                │
│  → Fetch hot posts                          │
│  → Save to JSON file (data/raw/)            │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Load (psycopg2)                            │
│  → Parse JSON                               │
│  → Insert into PostgreSQL                   │
│  → Handle duplicates (ON CONFLICT)          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  PostgreSQL Database                        │
│  Table: reddit_posts                        │
└─────────────────────────────────────────────┘
```

## Project Structure

```
reddit-data-pipeline/
├── pipeline.py                 # Main orchestrator
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Multi-container setup
├── .env                        # Database credentials
├── .gitignore                  # Git exclusions
├── data/
│   └── raw/                    # Extracted JSON files (timestamped)
├── src/
│   ├── extract/
│   │   └── extract_reddit.py   # Reddit data extraction
│   ├── load/
│   │   └── load_reddit.py      # Database loading
│   └── utils/
│       └── db_utils.py         # Database utilities
└── README.md                   # This file
```

## Prerequisites

- Docker Desktop installed and running
- Git

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/halilmertsenturk/reddit-data-pipeline.git
cd reddit-data-pipeline

# Build and run
docker-compose up --build

# In another terminal, verify data was loaded
docker exec reddit-postgres psql -U postgres -d reddit_pipeline -c "SELECT COUNT(*) FROM reddit_posts;"
```

### Option 2: Local Setup (Python + Docker)

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL container
docker run -d --name reddit-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine

# Create database
docker exec reddit-postgres psql -U postgres -c "CREATE DATABASE reddit_pipeline;"

# Create table
docker exec reddit-postgres psql -U postgres -d reddit_pipeline -c "
CREATE TABLE IF NOT EXISTS reddit_posts (
    post_id TEXT PRIMARY KEY,
    subreddit TEXT,
    title TEXT,
    author TEXT,
    score INT,
    num_comments INT,
    created_utc BIGINT,
    url TEXT
);"

# Run pipeline
python pipeline.py
```

## Database Schema

### Table: `reddit_posts`

| Column | Type | Notes |
|--------|------|-------|
| post_id | TEXT | Primary key (Reddit post ID) |
| subreddit | TEXT | Subreddit name |
| title | TEXT | Post title |
| author | TEXT | Post author |
| score | INT | Upvote score |
| num_comments | INT | Number of comments |
| created_utc | BIGINT | Unix timestamp |
| url | TEXT | Post URL |

## Usage

### Extract Data

```bash
python src/extract/extract_reddit.py
```

Fetches 10 hot posts from r/dataengineering and saves to `data/raw/reddit_posts_<timestamp>.json`

### Load Data

```bash
python src/load/load_reddit.py data/raw/reddit_posts_<timestamp>.json
```

Inserts posts from JSON file into PostgreSQL. Duplicates are ignored (ON CONFLICT DO NOTHING).

### Run Full Pipeline

```bash
python pipeline.py
```

Orchestrates extract → load in one command.

### Query Data

```bash
# Connect to database
docker exec -it reddit-postgres psql -U postgres -d reddit_pipeline

# View posts
SELECT post_id, title, author, score FROM reddit_posts LIMIT 10;

# Statistics
SELECT COUNT(*) as total_posts, COUNT(DISTINCT subreddit) as subreddits FROM reddit_posts;
```

## Environment Variables

Create a `.env` file in the root directory:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reddit_pipeline
DB_USER=postgres
DB_PASSWORD=postgres
```

For docker-compose, these are set in `docker-compose.yml`.

## Next Steps

- [ ] Add Apache Airflow for workflow orchestration
- [ ] Add dbt for data transformation
- [ ] Add data validation and quality checks
- [ ] Create Grafana dashboard for visualization
- [ ] Add scheduled runs (cron / Airflow DAGs)
- [ ] Multi-subreddit support
- [ ] Data retention policies

## Troubleshooting

### Connection refused
Ensure PostgreSQL container is running:
```bash
docker ps | grep reddit-postgres
```

### Permission denied on data/raw
```bash
mkdir -p data/raw
chmod 777 data/raw
```

### ModuleNotFoundError
Install dependencies:
```bash
pip install -r requirements.txt
```

## License

MIT
