from pydeequ.checks import Check, CheckLevel
from pydeequ.verification import VerificationResult, VerificationSuite
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder.appName("bronze-dq-customers").getOrCreate()
    try:
        customers = spark.table("lakehouse.bronze.customers")
        check = (Check(spark, CheckLevel.Error, "bronze customers")
                 .hasSize(lambda size: size > 0)
                 .isComplete("customer_id")
                 .isUnique("customer_id")
                 .isComplete("ingested_at"))
        result = (VerificationSuite(spark).onData(customers)
                  .addCheck(check).run())
        details = VerificationResult.checkResultsAsDataFrame(spark, result)
        details.show(truncate=False)
        if result.status != "Success":
            raise RuntimeError("Bronze customers DQ failed")
    finally:
        spark.sparkContext._gateway.shutdown_callback_server()
        spark.stop()


if __name__ == "__main__":
    main()
