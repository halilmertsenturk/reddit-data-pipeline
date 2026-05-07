# Reddit Data Engineering Pipeline

Complete end-to-end data engineering pipeline with Apache Airflow orchestration, dbt transformations, and Grafana visualization.

## Architecture

```
┌─────────────────────────────────────────┐
│  Reddit Public JSON API                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Apache Airflow (DAG Orchestration)     │
│  - Daily extraction at 00:00 UTC        │
│  - 2 retries on failure                 │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴───────┐
        │              │
        ▼              ▼
    Extract ──► Load ──┐
        │              │
        └──────────────┘
               │
               ▼
        ┌─────────────────┐
        │  PostgreSQL     │ ◄─── Raw Data
        │  reddit_posts   │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  dbt Transform  │
        │  Models & Tests │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    Staging  ────►  Marts (Fact Tables)
    Views            stg_reddit_posts
                     fct_reddit_posts
        │
        ▼
   ┌──────────────┐
   │  Grafana     │
   │  Dashboards  │
   │  & Alerts    │
   └──────────────┘
```

## Stack

- **Orchestration**: Apache Airflow 2.8.1
  - Daily DAG runs
  - Task dependencies and retries
  - Web UI at http://localhost:8080
  
- **Extraction**: Python + Requests
  - Reddit public JSON endpoints
  - No OAuth required
  
- **Loading**: PostgreSQL + psycopg2
  - Duplicate handling (ON CONFLICT)
  - Transaction support
  
- **Transformation**: dbt (Data Build Tool)
  - SQL-based transformations
  - Staging and mart layers
  - Data quality tests
  
- **Visualization**: Grafana
  - Real-time dashboards
  - PostgreSQL datasource integration
  - Admin UI at http://localhost:3000

## Quick Start

### Prerequisites
- Docker Desktop
- 4GB RAM available (Airflow + Grafana + PostgreSQL)

### Run Full Stack

```bash
git clone https://github.com/halilmertsenturk/reddit-data-pipeline.git
cd reddit-data-pipeline

docker-compose up --build
```

Wait for all services to start (2-3 minutes).

### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow | http://localhost:8080 | admin / admin |
| Grafana | http://localhost:3000 | admin / admin |
| PostgreSQL | localhost:5432 | postgres / postgres |

## Services

### PostgreSQL (Port 5432)
Raw Reddit data storage and transformations.

```bash
docker exec reddit-postgres psql -U postgres -d reddit_pipeline -c "SELECT COUNT(*) FROM reddit_posts;"
```

### Airflow (Port 8080)

**DAG**: `reddit_data_pipeline`

Tasks:
1. **extract_reddit**: Fetch 25 hot posts from r/dataengineering
2. **load_to_db**: Insert posts into PostgreSQL
3. **dbt_transformations**: 
   - dbt_parse: Validate models
   - dbt_run: Execute transformations
   - dbt_test: Run data quality tests

Schedule: Daily at 00:00 UTC

Manual trigger:
```bash
docker exec airflow-scheduler airflow dags trigger reddit_data_pipeline
```

View logs:
```bash
docker exec airflow-webserver airflow logs reddit_data_pipeline extract_reddit
```

### dbt (Runs within Airflow)

Models:
- **stg_reddit_posts** (VIEW): Staging layer with cleaned data
- **fct_reddit_posts** (TABLE): Fact table with engagement metrics

Run manually:
```bash
docker exec reddit-pipeline dbt run --profiles-dir /app/dbt
```

Test data quality:
```bash
docker exec reddit-pipeline dbt test --profiles-dir /app/dbt
```

### Grafana (Port 3000)

**Features**:
- PostgreSQL datasource preconfigured
- Build custom dashboards from reddit_posts table
- Real-time post metrics
- Engagement level analysis

**Sample Queries**:

Top posts by score:
```sql
SELECT author, title, score 
FROM fct_reddit_posts 
ORDER BY score DESC LIMIT 10
```

Engagement distribution:
```sql
SELECT engagement_level, COUNT(*) 
FROM fct_reddit_posts 
GROUP BY engagement_level
```

## Database Schema

### Raw Layer (reddit_posts)
| Column | Type | Notes |
|--------|------|-------|
| post_id | TEXT PRIMARY KEY | Reddit post ID |
| subreddit | TEXT | Subreddit name |
| title | TEXT | Post title |
| author | TEXT | Post author |
| score | INT | Upvote score |
| num_comments | INT | Comment count |
| created_utc | BIGINT | Unix timestamp |
| url | TEXT | Post URL |

### Staging Layer (stg_reddit_posts) - VIEW
Adds `loaded_at` timestamp.

### Mart Layer (fct_reddit_posts) - TABLE
Adds:
- `engagement_level`: viral / popular / trending / normal (based on score)
- `rank_in_subreddit`: Row number within subreddit

## Project Structure

```
reddit-data-pipeline/
├── dags/
│   └── reddit_pipeline_dag.py          # Airflow DAG definition
├── dbt/
│   ├── dbt_project.yml                 # dbt config
│   ├── profiles.yml                    # dbt profiles
│   └── models/
│       ├── staging/
│       │   └── stg_reddit_posts.sql
│       ├── marts/
│       │   └── fct_reddit_posts.sql
│       └── schema.yml                  # dbt tests & docs
├── grafana/
│   ├── datasources.yml                 # Grafana data source config
│   └── grafana.env                     # Grafana environment
├── src/
│   ├── extract/extract_reddit.py
│   ├── load/load_reddit.py
│   └── utils/db_utils.py
├── data/raw/                           # Extracted JSON files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

## Troubleshooting

### Airflow fails to start
```bash
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

### dbt models not running
Check dbt profiles.yml connection:
```bash
docker exec reddit-pipeline dbt debug --profiles-dir /app/dbt
```

### Grafana won't connect to PostgreSQL
Verify datasource in Grafana UI → Configuration → Data Sources. Use `postgres` as hostname.

### Port already in use
```bash
docker-compose down -v
docker system prune
docker-compose up --build
```

## Next Steps

- [ ] Add data quality alerts in Airflow
- [ ] Create Grafana dashboards for monitoring
- [ ] Add Slack notifications on DAG failures
- [ ] Implement incremental loading for large datasets
- [ ] Add multi-subreddit support
- [ ] Deploy to Kubernetes or cloud (AWS/GCP)
- [ ] Add CI/CD with GitHub Actions
- [ ] Implement data lineage tracking

## Performance Tips

- Increase Airflow parallelism in docker-compose
- Use connection pooling in PostgreSQL
- Optimize dbt models with incremental loading
- Archive old data to S3/object storage
- Use Grafana caching for frequent queries

## License

MIT
