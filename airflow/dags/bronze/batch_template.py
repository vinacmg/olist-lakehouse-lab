from datetime import datetime, timedelta

from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.sdk import DAG


JARS = ",".join((
    "/opt/spark/jars/iceberg-spark-runtime.jar",
    "/opt/spark/jars/iceberg-aws-bundle.jar",
    "/opt/spark/jars/postgresql.jar",
    "/opt/spark/jars/deequ.jar",
))

SPARK_OPERATOR_DEFAULTS = {
    "conn_id": "spark_default",
    "deploy_mode": "client",
    "properties_file": "/opt/spark/conf/spark-defaults.conf",
    "jars": JARS,
    "conf": {
        "spark.driver.host": "airflow-scheduler",
        "spark.driver.bindAddress": "0.0.0.0",
    },
}


def create_bronze_batch_dag(*, table_name, load_application, dq_application):
    with DAG(
        dag_id=f"bronze_batch_{table_name}",
        description=f"Load and validate the {table_name} Bronze snapshot.",
        schedule=None,
        start_date=datetime(2026, 8, 29),
        catchup=False,
        default_args={
            "retries": 1,
            "retry_delay": timedelta(minutes=1),
        },
        tags=["olist", "spark", "bronze", "batch", table_name],
    ) as dag:
        load = SparkSubmitOperator(
            task_id=f"load_{table_name}",
            application=load_application,
            name=f"bronze-batch-{table_name}",
            **SPARK_OPERATOR_DEFAULTS,
        )

        validate = SparkSubmitOperator(
            task_id=f"dq_{table_name}",
            application=dq_application,
            name=f"bronze-dq-{table_name}",
            **SPARK_OPERATOR_DEFAULTS,
        )

        load >> validate

    return dag
