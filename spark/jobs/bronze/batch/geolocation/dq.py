from pydeequ.checks import Check, CheckLevel
from pydeequ.verification import VerificationResult, VerificationSuite
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder.appName("bronze-dq-geolocation").getOrCreate()
    try:
        geolocation = spark.table("lakehouse.bronze.geolocation")
        check = (Check(spark, CheckLevel.Error, "bronze geolocation")
                 .hasSize(lambda size: size > 0)
                 .isComplete("geolocation_id")
                 .isUnique("geolocation_id")
                 .isComplete("ingested_at"))
        result = (VerificationSuite(spark).onData(geolocation)
                  .addCheck(check).run())
        details = VerificationResult.checkResultsAsDataFrame(spark, result)
        details.show(truncate=False)
        if result.status != "Success":
            raise RuntimeError("Bronze geolocation DQ failed")
    finally:
        spark.sparkContext._gateway.shutdown_callback_server()
        spark.stop()


if __name__ == "__main__":
    main()
