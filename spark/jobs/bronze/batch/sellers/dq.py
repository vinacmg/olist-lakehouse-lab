from pydeequ.checks import Check, CheckLevel
from pydeequ.verification import VerificationResult, VerificationSuite
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder.appName("bronze-dq-sellers").getOrCreate()
    try:
        sellers = spark.table("lakehouse.bronze.sellers")
        check = (Check(spark, CheckLevel.Error, "bronze sellers")
                 .hasSize(lambda size: size > 0)
                 .isComplete("seller_id")
                 .isUnique("seller_id")
                 .isComplete("ingested_at"))
        result = (VerificationSuite(spark).onData(sellers)
                  .addCheck(check).run())
        details = VerificationResult.checkResultsAsDataFrame(spark, result)
        details.show(truncate=False)
        if result.status != "Success":
            raise RuntimeError("Bronze sellers DQ failed")
    finally:
        spark.sparkContext._gateway.shutdown_callback_server()
        spark.stop()


if __name__ == "__main__":
    main()
