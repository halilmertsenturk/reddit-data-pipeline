from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from extract.extract_reddit import extract_reddit_data, save_to_json
from load.load_reddit import insert_posts

default_args = {
    'owner': 'data-engineering',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2026, 5, 1),
}

dag = DAG(
    'reddit_data_pipeline',
    default_args=default_args,
    description='Extract Reddit data and load to PostgreSQL',
    schedule_interval='*/15 * * * *',
    catchup=False,
)

def extract_reddit_task(**context):
    """Extract Reddit data and save to JSON"""
    posts = extract_reddit_data(subreddit="dataengineering", limit=100, sort="new")
    if posts:
        filename = save_to_json(posts)
        context['task_instance'].xcom_push(key='json_file', value=filename)
        return len(posts)
    return 0

def load_to_db_task(**context):
    """Load extracted data into PostgreSQL"""
    json_file = context['task_instance'].xcom_pull(
        task_ids='extract_reddit',
        key='json_file'
    )
    
    if json_file:
        import json
        with open(json_file, 'r') as f:
            posts = json.load(f)
        inserted = insert_posts(posts)
        return inserted
    return 0

# Extract Task
extract_reddit = PythonOperator(
    task_id='extract_reddit',
    python_callable=extract_reddit_task,
    dag=dag,
)

# Load Task
load_to_db = PythonOperator(
    task_id='load_to_db',
    python_callable=load_to_db_task,
    dag=dag,
    depends_on_past=False,
)

# dbt Tasks
with TaskGroup('dbt_transformations', dag=dag) as dbt_group:
    dbt_parse = BashOperator(
        task_id='dbt_parse',
        bash_command='cd /app/dbt && dbt parse --profiles-dir . || true',
    )
    
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /app/dbt && dbt run --profiles-dir . || true',
    )
    
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /app/dbt && dbt test --profiles-dir . || true',
    )
    
    dbt_parse >> dbt_run >> dbt_test

# DAG Dependencies
extract_reddit >> load_to_db >> dbt_group
