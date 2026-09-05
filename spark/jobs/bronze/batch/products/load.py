import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


def main():
    spark = (SparkSession.builder.appName("bronze-batch-products")
             .config("spark.sql.sources.partitionOverwriteMode", "static")
             .getOrCreate())
    try:
        products = (spark.read.format("jdbc")
                    .option("url", f"jdbc:postgresql://postgres:5432/{os.environ['POSTGRES_DB']}")
                    .option("dbtable", "ecommerce.products")
                    .option("user", os.environ["POSTGRES_USER"])
                    .option("password", os.environ["POSTGRES_PASSWORD"])
                    .option("driver", "org.postgresql.Driver").load()
                    .withColumn("ingested_at", current_timestamp()))
        products.createOrReplaceTempView("products_batch")
        spark.sql("""
            INSERT OVERWRITE TABLE lakehouse.bronze.products
            SELECT product_id, category_name, name_length, description_length,
                   photos_qty, weight_g, length_cm, height_cm, width_cm,
                   ingested_at
            FROM products_batch
        """)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
