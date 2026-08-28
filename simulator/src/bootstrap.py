import argparse
from pathlib import Path

import pandas as pd
import psycopg

from db import insert_rows, prepare_rows


STATIC_TABLES = (
    (
        "customers",
        "olist_customers_dataset.csv",
        ("customer_id", "customer_unique_id"),
        (
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ),
        ("customer_id", "customer_unique_id", "zip_code_prefix", "city", "state"),
    ),
    (
        "products",
        "olist_products_dataset.csv",
        ("product_id",),
        (
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ),
        (
            "product_id",
            "category_name",
            "name_length",
            "description_length",
            "photos_qty",
            "weight_g",
            "length_cm",
            "height_cm",
            "width_cm",
        ),
    ),
    (
        "sellers",
        "olist_sellers_dataset.csv",
        ("seller_id",),
        ("seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"),
        ("seller_id", "zip_code_prefix", "city", "state"),
    ),
    (
        "geolocation",
        "olist_geolocation_dataset.csv",
        (),
        (
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ),
        ("zip_code_prefix", "lat", "lng", "city", "state"),
    ),
)


def run_bootstrap(data_dir, dsn, limit=None, chunk_size=5000):
    data_dir = Path(data_dir)

    with psycopg.connect(dsn) as conn:
        for table, filename, uuid_columns, csv_columns, db_columns in STATIC_TABLES:
            dataframe = pd.read_csv(data_dir / filename, usecols=list(csv_columns))
            if limit is not None:
                dataframe = dataframe.head(limit)

            rows = prepare_rows(dataframe, uuid_columns)
            inserted = insert_rows(conn, table, db_columns, rows, chunk_size)
            print(f"{table}: {inserted:,} rows inserted")

        # One transaction: a failure leaves no partially completed bootstrap.
        conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Load non-temporal Olist data once.")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--chunk-size", type=int, default=5000)
    args = parser.parse_args()
    run_bootstrap(args.data_dir, args.dsn, args.limit, args.chunk_size)


if __name__ == "__main__":
    main()

