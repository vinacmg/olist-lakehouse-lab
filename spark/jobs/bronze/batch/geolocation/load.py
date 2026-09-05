import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


def main():
    spark = (SparkSession.builder.appName("bronze-batch-geolocation")
             .config("spark.sql.sources.partitionOverwriteMode", "static")
             .getOrCreate())
    try:
        geolocation = (spark.read.format("jdbc")
                       .option("url", f"jdbc:postgresql://postgres:5432/{os.environ['POSTGRES_DB']}")
                       .option("dbtable", "ecommerce.geolocation")
                       .option("user", os.environ["POSTGRES_USER"])
                       .option("password", os.environ["POSTGRES_PASSWORD"])
                       .option("driver", "org.postgresql.Driver").load()
                       .withColumn("ingested_at", current_timestamp()))
        geolocation.createOrReplaceTempView("geolocation_batch")
        spark.sql("""
            INSERT OVERWRITE TABLE lakehouse.bronze.geolocation
            SELECT geolocation_id, zip_code_prefix, lat, lng, city, state,
                   ingested_at
            FROM geolocation_batch
        """)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
