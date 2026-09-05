ARG AIRFLOW_VERSION
FROM apache/airflow:${AIRFLOW_VERSION}

USER root

ARG AIRFLOW_VERSION
ARG AIRFLOW_SPARK_PROVIDER_VERSION
ARG SPARK_VERSION
ARG ICEBERG_VERSION
ARG POSTGRES_JDBC_VERSION
ARG DEEQU_VERSION
ARG PYDEEQU_COMMIT

RUN apt-get update \
 && apt-get install --no-install-recommends -y openjdk-17-jre-headless curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /opt/spark/conf /opt/spark/jars /opt/pyspark-home \
 && chown airflow:0 /opt/pyspark-home

RUN curl -fL \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.0_2.13/${ICEBERG_VERSION}/iceberg-spark-runtime-4.0_2.13-${ICEBERG_VERSION}.jar" \
    -o "/opt/spark/jars/iceberg-spark-runtime.jar" \
 && curl -fL \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/${ICEBERG_VERSION}/iceberg-aws-bundle-${ICEBERG_VERSION}.jar" \
    -o "/opt/spark/jars/iceberg-aws-bundle.jar" \
 && curl -fL \
    "https://repo1.maven.org/maven2/org/postgresql/postgresql/${POSTGRES_JDBC_VERSION}/postgresql-${POSTGRES_JDBC_VERSION}.jar" \
    -o "/opt/spark/jars/postgresql.jar" \
 && curl -fL \
    "https://repo1.maven.org/maven2/com/amazon/deequ/deequ/${DEEQU_VERSION}/deequ-${DEEQU_VERSION}.jar" \
    -o "/opt/spark/jars/deequ.jar"

COPY spark/conf/spark-defaults.conf /opt/spark/conf/spark-defaults.conf
USER airflow

RUN curl -fL \
    "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.12.txt" \
    -o /tmp/airflow-constraints.txt \
 && curl -fL \
    "https://github.com/awslabs/python-deequ/archive/${PYDEEQU_COMMIT}.tar.gz" \
    -o /tmp/pydeequ.tar.gz \
 && sed -i \
    -e '/^apache-airflow-providers-apache-spark==/d' \
    -e '/^pyspark==/d' \
    /tmp/airflow-constraints.txt \
 && pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    "apache-airflow-providers-apache-spark==${AIRFLOW_SPARK_PROVIDER_VERSION}" \
    "pyspark==${SPARK_VERSION}" \
    /tmp/pydeequ.tar.gz \
    --constraint /tmp/airflow-constraints.txt \
 && pip check \
 && ln -s "$(python -c 'import pathlib, pyspark; print(pathlib.Path(pyspark.__file__).parent)')" \
    /opt/pyspark-home/current \
 && rm /tmp/airflow-constraints.txt /tmp/pydeequ.tar.gz

ENV SPARK_HOME=/opt/pyspark-home/current
ENV PATH="${SPARK_HOME}/bin:${PATH}"
