import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


def main():
    spark = (SparkSession.builder.appName("bronze-batch-sellers")
             .config("spark.sql.sources.partitionOverwriteMode", "static")
             .getOrCreate())
    try:
        sellers = (spark.read.format("jdbc")
                   .option("url", f"jdbc:postgresql://postgres:5432/{os.environ['POSTGRES_DB']}")
                   .option("dbtable", "ecommerce.sellers")
                   .option("user", os.environ["POSTGRES_USER"])
                   .option("password", os.environ["POSTGRES_PASSWORD"])
                   .option("driver", "org.postgresql.Driver").load()
                   .withColumn("ingested_at", current_timestamp()))
        sellers.createOrReplaceTempView("sellers_batch")
        spark.sql("""
            INSERT OVERWRITE TABLE lakehouse.bronze.sellers
            SELECT seller_id, zip_code_prefix, city, state, ingested_at
            FROM sellers_batch
        """)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
