# Airflow DAG definition.
from bronze.batch_template import create_bronze_batch_dag


dag = create_bronze_batch_dag(
    table_name="products",
    load_application="/opt/spark/jobs/bronze/batch/products/load.py",
    dq_application="/opt/spark/jobs/bronze/batch/products/dq.py",
)
