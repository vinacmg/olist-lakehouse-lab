import argparse
import uuid
from pathlib import Path

import pandas as pd
import psycopg


# ---------- Utils ----------

def hex_to_uuid_or_none(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return uuid.UUID(hex=s) if len(s) == 32 else uuid.UUID(s)


def prepare_rows(df, id_cols):
    df = df.copy()

    for col in id_cols:
        df[col] = df[col].apply(hex_to_uuid_or_none)

    # pandas NaN -> Python None (Postgres NULL)
    df = df.where(pd.notnull(df), None)

    return [tuple(r) for r in df.itertuples(index=False, name=None)]


def insert_batch(conn, table, columns, rows):
    if not rows:
        return 0

    placeholders = ", ".join(["%s"] * len(columns))
    cols = ", ".join([f'"{c}"' for c in columns])

    query = f'INSERT INTO "{table}" ({cols}) VALUES ({placeholders});'

    with conn.cursor() as cur:
        cur.executemany(query, rows)

    return len(rows)


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--chunk-size", type=int, default=5000)

    args = parser.parse_args()
    data_dir = Path(args.data_dir)

    tables = [
        (
            "customers",
            "olist_customers_dataset.csv",
            ["customer_id", "customer_unique_id"],
            ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"],
            ["customer_id", "customer_unique_id", "zip_code_prefix", "city", "state"],
        ),
        (
            "sellers",
            "olist_sellers_dataset.csv",
            ["seller_id"],
            ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
            ["seller_id", "zip_code_prefix", "city", "state"],
        ),
        (
            "products",
            "olist_products_dataset.csv",
            ["product_id"],
            [
                "product_id",
                "product_category_name",
                "product_name_lenght",
                "product_description_lenght",
                "product_photos_qty",
                "product_weight_g",
                "product_length_cm",
                "product_height_cm",
                "product_width_cm",
            ],
            [
                "product_id",
                "category_name",
                "name_length",
                "description_length",
                "photos_qty",
                "weight_g",
                "length_cm",
                "height_cm",
                "width_cm",
            ],
        ),
    ]

    with psycopg.connect(args.dsn) as conn:
        for table, csv_file, id_cols, csv_cols, db_cols in tables:
            print(f"\n==> Loading {table}")

            df = pd.read_csv(data_dir / csv_file)

            if args.limit:
                df = df.head(args.limit)

            df = df[csv_cols]
            rows = prepare_rows(df, id_cols)

            inserted = 0
            for i in range(0, len(rows), args.chunk_size):
                batch = rows[i : i + args.chunk_size]
                inserted += insert_batch(conn, table, db_cols, batch)

            conn.commit()
            print(f"Inserted {inserted:,} rows")


if __name__ == "__main__":
    main()