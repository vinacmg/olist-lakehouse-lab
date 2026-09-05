CREATE TABLE IF NOT EXISTS lakehouse.bronze.reviews (
    review_id UUID NOT NULL,
    order_id UUID NOT NULL,
    score INTEGER NOT NULL,
    comment_title VARCHAR,
    comment_message VARCHAR,
    created_at TIMESTAMP(6) WITH TIME ZONE NOT NULL,
    answered_at TIMESTAMP(6) WITH TIME ZONE,
    cdc_operation VARCHAR NOT NULL,
    cdc_event_at TIMESTAMP(6) WITH TIME ZONE,
    ingested_at TIMESTAMP(6) WITH TIME ZONE NOT NULL
)
COMMENT 'Bronze mirror of ecommerce.reviews from PostgreSQL.'
WITH (
    format = 'PARQUET',
    format_version = 3,
    compression_codec = 'SNAPPY',
    object_store_layout_enabled = true,
    target_max_file_size = '128MB'
);
