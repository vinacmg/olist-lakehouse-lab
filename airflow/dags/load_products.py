from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator


JARS = ",".join(
    (
        "/opt/spark/jars/iceberg-spark-runtime.jar",
        "/opt/spark/jars/iceberg-aws-bundle.jar",
        "/opt/spark/jars/postgresql.jar",
    )
)


with DAG(
    dag_id="load_products",
    description="Load the existing Olist products table into Iceberg bronze.",
    schedule=None,
    start_date=datetime(2026, 8, 29),
    catchup=False,
    tags=["olist", "spark", "bronze"],
) as dag:
    SparkSubmitOperator(
        task_id="load_products",
        conn_id="spark_default",
        application="/opt/spark/jobs/batch/load_products.py",
        deploy_mode="client",
        properties_file="/opt/spark/conf/spark-defaults.conf",
        jars=JARS,
        conf={
            "spark.driver.host": "airflow-scheduler",
            "spark.driver.bindAddress": "0.0.0.0",
        }
    )
