from datetime import datetime
import subprocess

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator

from docker.types import Mount


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
}


def run_elt_script():
    script_path = "/opt/airflow/elt_script/elt_script.py"

    result = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(
            f"Script failed with error: {result.stderr}"
        )

    print(result.stdout)


with DAG(
    dag_id="elt_and_dbt",
    default_args=default_args,
    description="An ELT workflow with dbt",
    start_date=datetime(2023, 10, 3),
    schedule=None,
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id="run_elt_script",
        python_callable=run_elt_script,
    )

    t2 = DockerOperator(
        task_id="dbt_run",
        image="ghcr.io/dbt-labs/dbt-postgres:1.4.7",

        command=[
            "run",
            "--profiles-dir",
            "/root",
            "--project-dir",
            "/dbt",
            "--full-refresh",
        ],

        auto_remove="success",

        docker_url="unix://var/run/docker.sock",

        network_mode="p_elt_elt_network",

        mounts=[
            Mount(
                source="C:/Users/abbig/P_ELT/postgres_transformations",
                target="/dbt",
                type="bind",
            ),
            Mount(
                source="C:/Users/abbig/.dbt",
                target="/root",
                type="bind",
            ),
        ],
    )

    t1 >> t2