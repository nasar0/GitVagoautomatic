from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from automatic_git_vago import crearInterfaz , mostrar_carpetas
crearInterfaz()
default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1),
}

with DAG(
    dag_id="primer_dag_etl",
    schedule_interval="@daily",  # Corre una vez al día
    default_args=default_args,
    catchup=False,
    description="Git Vago Automatic",
) as dag:
    data = mostrar_carpetas()

   