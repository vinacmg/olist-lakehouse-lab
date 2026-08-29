import os

from pyspark.sql import SparkSession


def main():
    spark = (
        SparkSession.builder
        .appName("load-products")
        .getOrCreate()
    )

    jdbc_url = (
        f"jdbc:postgresql://postgres:5432/"
        f"{os.environ['POSTGRES_DB']}"
    )

    products = (
        spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", "ecommerce.products")
        .option("user", os.environ["POSTGRES_USER"])
        .option("password", os.environ["POSTGRES_PASSWORD"])
        .option("driver", "org.postgresql.Driver")
        .load()
    )

    products.writeTo(
        "lakehouse.bronze.products"
    ).createOrReplace()

    spark.stop()


if __name__ == "__main__":
    main()