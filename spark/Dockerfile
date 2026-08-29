FROM apache/spark:4.0.1

USER root

ARG ICEBERG_VERSION=1.11.0
ARG POSTGRES_JDBC_VERSION=42.7.7

RUN mkdir -p /opt/spark/jobs /opt/spark/conf

RUN curl -fL \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.0_2.13/${ICEBERG_VERSION}/iceberg-spark-runtime-4.0_2.13-${ICEBERG_VERSION}.jar" \
    -o /opt/spark/jars/iceberg-spark-runtime-4.0_2.13-${ICEBERG_VERSION}.jar \
 && curl -fL \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar" \
    -o /opt/spark/jars/iceberg-aws-bundle-${ICEBERG_VERSION}.jar \
 && curl -fL \
    "https://repo1.maven.org/maven2/org/postgresql/postgresql/${POSTGRES_JDBC_VERSION}/postgresql-${POSTGRES_JDBC_VERSION}.jar" \
    -o /opt/spark/jars/postgresql-${POSTGRES_JDBC_VERSION}.jar

ENV PATH="/opt/spark/bin:${PATH}"

COPY conf/spark-defaults.conf /opt/spark/conf/spark-defaults.conf

USER spark