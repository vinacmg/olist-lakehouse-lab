import uuid

import pandas as pd


def to_uuid(value):
    """Convert an Olist identifier to UUID, preserving missing values as NULL."""
    if pd.isna(value):
        return None
    text = str(value).strip()
    return uuid.UUID(hex=text) if len(text) == 32 else uuid.UUID(text)


def prepare_rows(dataframe, uuid_columns=()):
    """Return DB-ready tuples without imputing or cleaning source values."""
    dataframe = dataframe.copy()

    for column in uuid_columns:
        dataframe[column] = dataframe[column].apply(to_uuid)

    # Object dtype is required for pandas to keep Python None instead of NaN/NaT.
    dataframe = dataframe.astype(object).where(pd.notna(dataframe), None)
    return list(dataframe.itertuples(index=False, name=None))


def insert_rows(conn, table, columns, rows, chunk_size=5000):
    if not rows:
        return 0

    quoted_columns = ", ".join(f'"{column}"' for column in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    query = f'INSERT INTO ecommerce.{table} ({quoted_columns}) VALUES ({placeholders})'

    with conn.cursor() as cursor:
        for start in range(0, len(rows), chunk_size):
            cursor.executemany(query, rows[start : start + chunk_size])

    return len(rows)


def update_order(conn, order_id, status, timestamp_column=None, occurred_at=None):
    with conn.cursor() as cursor:
        if timestamp_column is None:
            cursor.execute(
                "UPDATE ecommerce.orders SET status = %s WHERE order_id = %s",
                (status, order_id),
            )
        else:
            allowed_columns = {
                "approved_at",
                "delivered_carrier_at",
                "delivered_customer_at",
            }
            if timestamp_column not in allowed_columns:
                raise ValueError(f"Unsupported order timestamp: {timestamp_column}")
            cursor.execute(
                f'UPDATE ecommerce.orders SET status = %s, "{timestamp_column}" = %s WHERE order_id = %s',
                (status, occurred_at, order_id),
            )

def update_review_answer(conn, review_id, order_id, answered_at):
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE ecommerce.reviews SET answered_at = %s WHERE review_id = %s AND order_id = %s",
            (answered_at, review_id, order_id),
        )