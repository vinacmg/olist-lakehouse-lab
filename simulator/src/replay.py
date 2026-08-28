import argparse
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg

from db import insert_rows, prepare_rows, to_uuid, update_order, update_review_answer


@dataclass(order=True)
class Event:
    occurred_at: datetime
    sequence: int
    kind: str
    payload: object


def _timestamp(value):
    return None if pd.isna(value) else value.to_pydatetime()


def _read_csv(data_dir, filename, **kwargs):
    return pd.read_csv(Path(data_dir) / filename, **kwargs)


def build_events(data_dir, limit=None):
    orders = _read_csv(
        data_dir,
        "olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    ).sort_values("order_purchase_timestamp")

    if limit is not None:
        orders = orders.head(limit)

    selected_order_ids = set(orders["order_id"])

    items = _read_csv(
        data_dir,
        "olist_order_items_dataset.csv",
        parse_dates=["shipping_limit_date"],
    )

    payments = _read_csv(
        data_dir,
        "olist_order_payments_dataset.csv",
    )

    reviews = _read_csv(
        data_dir,
        "olist_order_reviews_dataset.csv",
        parse_dates=[
            "review_creation_date",
            "review_answer_timestamp",
        ],
    )

    items = items[items["order_id"].isin(selected_order_ids)]
    payments = payments[payments["order_id"].isin(selected_order_ids)]
    reviews = reviews[reviews["order_id"].isin(selected_order_ids)]

    items_by_order = {
        order_id: dataframe
        for order_id, dataframe in items.groupby("order_id")
    }

    payments_by_order = {
        order_id: dataframe
        for order_id, dataframe in payments.groupby("order_id")
    }

    purchase_by_order = {
        order["order_id"]: _timestamp(order["order_purchase_timestamp"])
        for _, order in orders.iterrows()
    }

    events = []
    sequence = 0

    def add(occurred_at, kind, payload):
        nonlocal sequence

        if occurred_at is not None:
            events.append(
                Event(
                    occurred_at=occurred_at,
                    sequence=sequence,
                    kind=kind,
                    payload=payload,
                )
            )
            sequence += 1

    for _, order in orders.iterrows():
        order_id = order["order_id"]

        add(
            _timestamp(order["order_purchase_timestamp"]),
            "purchase",
            order,
        )

        add(
            _timestamp(order["order_approved_at"]),
            "approved",
            order_id,
        )

        add(
            _timestamp(order["order_delivered_carrier_date"]),
            "shipped",
            order_id,
        )

        add(
            _timestamp(order["order_delivered_customer_date"]),
            "delivered",
            order_id,
        )

        if order["order_status"] in {"canceled", "unavailable"}:
            # The source has a final status but no timestamp for this transition.
            # Apply it after the last timestamped event, without inventing a date.
            known_events = [
                _timestamp(order["order_purchase_timestamp"]),
                _timestamp(order["order_approved_at"]),
                _timestamp(order["order_delivered_carrier_date"]),
                _timestamp(order["order_delivered_customer_date"]),
            ]

            last_known_at = max(
                value
                for value in known_events
                if value is not None
            )

            add(
                last_known_at,
                order["order_status"],
                order_id,
            )

    for _, review in reviews.iterrows():
        review_timestamp = _timestamp(review["review_creation_date"])
        purchase_timestamp = purchase_by_order[review["order_id"]]

        # Some reviews precede the purchase timestamp in the source data.
        # Delay the insert until the order exists but preserving the original data.
        review_insert_timestamp = (
            max(review_timestamp, purchase_timestamp)
            if review_timestamp is not None
            else purchase_timestamp
        )

        add(
            review_insert_timestamp,
            "review_created",
            review,
        )

        add(
            _timestamp(review["review_answer_timestamp"]),
            "review_answered",
            review,
        )

    return sorted(events), items_by_order, payments_by_order


def apply_event(conn, event, items_by_order, payments_by_order):
    if event.kind == "purchase":
        order = event.payload
        order_id_text = order["order_id"]

        order_row = [[
            to_uuid(order_id_text),
            to_uuid(order["customer_id"]),
            "created",
            _timestamp(order["order_purchase_timestamp"]),
            None,
            None,
            None,
            _timestamp(order["order_estimated_delivery_date"]),
        ]]

        insert_rows(
            conn,
            "orders",
            (
                "order_id",
                "customer_id",
                "status",
                "purchased_at",
                "approved_at",
                "delivered_carrier_at",
                "delivered_customer_at",
                "estimated_delivery_at",
            ),
            order_row,
        )

        if order_id_text in items_by_order:
            dataframe = items_by_order[order_id_text][[
                "order_id",
                "order_item_id",
                "product_id",
                "seller_id",
                "shipping_limit_date",
                "price",
                "freight_value",
            ]]

            rows = prepare_rows(
                dataframe,
                ("order_id", "product_id", "seller_id"),
            )

            insert_rows(
                conn,
                "items",
                (
                    "order_id",
                    "item_id",
                    "product_id",
                    "seller_id",
                    "shipping_limit_at",
                    "price",
                    "freight_value",
                ),
                rows,
            )

        return

    if event.kind == "approved":
        order_id_text = event.payload

        update_order(
            conn,
            to_uuid(order_id_text),
            "approved",
            "approved_at",
            event.occurred_at,
        )

        if order_id_text in payments_by_order:
            dataframe = payments_by_order[order_id_text][[
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value",
            ]]

            rows = prepare_rows(
                dataframe,
                ("order_id",),
            )

            insert_rows(
                conn,
                "payments",
                (
                    "order_id",
                    "payment_sequential",
                    "type",
                    "installments",
                    "value",
                ),
                rows,
            )

        return

    if event.kind == "shipped":
        update_order(
            conn,
            to_uuid(event.payload),
            "shipped",
            "delivered_carrier_at",
            event.occurred_at,
        )
        return

    if event.kind == "delivered":
        update_order(
            conn,
            to_uuid(event.payload),
            "delivered",
            "delivered_customer_at",
            event.occurred_at,
        )
        return

    if event.kind == "canceled":
        update_order(
            conn,
            to_uuid(event.payload),
            "canceled",
        )
        return

    if event.kind == "unavailable":
        update_order(
            conn,
            to_uuid(event.payload),
            "unavailable",
        )
        return

    review = event.payload

    if event.kind == "review_created":
        row = [[
            to_uuid(review["review_id"]),
            to_uuid(review["order_id"]),
            review["review_score"],
            review["review_comment_title"],
            review["review_comment_message"],
            _timestamp(review["review_creation_date"]),
            None,
        ]]

        row = [[
            None if pd.isna(value) else value
            for value in row[0]
        ]]

        insert_rows(
            conn,
            "reviews",
            (
                "review_id",
                "order_id",
                "score",
                "comment_title",
                "comment_message",
                "created_at",
                "answered_at",
            ),
            row,
        )

    elif event.kind == "review_answered":
        update_review_answer(
            conn,
            to_uuid(review["review_id"]),
            to_uuid(review["order_id"]),
            _timestamp(review["review_answer_timestamp"]),
        )


def _paced(events, speed):
    """Yield events while mapping source time to wall-clock time."""
    iterator = iter(events)
    try:
        previous_event = next(iterator)
    except StopIteration:
        return

    yield previous_event

    for event in iterator:
        source_seconds = (event.occurred_at - previous_event.occurred_at).total_seconds()
        time.sleep(max(0, source_seconds / speed))
        yield event
        previous_event = event


def run_replay(
    data_dir,
    dsn,
    limit=None,
    speed=0.0,
    log_every=1000,
):
    events, items_by_order, payments_by_order = build_events(
        data_dir,
        limit,
    )

    events_to_apply = (
        events
        if speed <= 0
        else _paced(events, speed)
    )

    total_events = len(events)

    print(f"Starting replay: {total_events:,} events")

    with psycopg.connect(dsn) as conn:
        for processed_events, event in enumerate(
            events_to_apply,
            start=1,
        ):
            apply_event(
                conn,
                event,
                items_by_order,
                payments_by_order,
            )

            conn.commit()

            if log_every and processed_events % log_every == 0:
                progress = processed_events / total_events * 100

                print(
                    f"Replay progress: "
                    f"{processed_events:,}/{total_events:,} "
                    f"({progress:.1f}%) "
                    f"- {event.occurred_at}"
                )

    print(f"Replay completed: {total_events:,} events applied")


def main():
    parser = argparse.ArgumentParser(description="Replay temporal Olist events.")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--limit", type=int, help="Number of orders to replay")
    parser.add_argument("--speed", type=float, default=0.0, help="Source seconds per real second; 0 runs immediately")
    parser.add_argument("--log-every", type=int, default=1000, help="Log replay progress every N events; 0 disables progress logs")
    args = parser.parse_args()
    run_replay(args.data_dir, args.dsn, args.limit, args.speed, args.log_every)


if __name__ == "__main__":
    main()
