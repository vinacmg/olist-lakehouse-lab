from pydeequ.checks import Check, CheckLevel
from pydeequ.verification import VerificationResult, VerificationSuite
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder.appName("bronze-dq-products").getOrCreate()
    try:
        products = spark.table("lakehouse.bronze.products")
        check = (Check(spark, CheckLevel.Error, "bronze products")
                 .hasSize(lambda size: size > 0)
                 .isComplete("product_id")
                 .isUnique("product_id")
                 .isComplete("ingested_at"))
        result = (VerificationSuite(spark).onData(products)
                  .addCheck(check).run())
        details = VerificationResult.checkResultsAsDataFrame(spark, result)
        details.show(truncate=False)
        if result.status != "Success":
            raise RuntimeError("Bronze products DQ failed")
    finally:
        spark.sparkContext._gateway.shutdown_callback_server()
        spark.stop()


if __name__ == "__main__":
    main()
