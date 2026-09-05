CREATE TABLE IF NOT EXISTS lakehouse.bronze.customers (
    customer_id UUID NOT NULL,
    customer_unique_id UUID NOT NULL,
    zip_code_prefix INTEGER NOT NULL,
    city VARCHAR NOT NULL,
    state VARCHAR NOT NULL,
    ingested_at TIMESTAMP(6) WITH TIME ZONE NOT NULL
)
COMMENT 'Bronze mirror of ecommerce.customers from PostgreSQL.'
WITH (
    format = 'PARQUET',
    format_version = 3,
    compression_codec = 'SNAPPY',
    object_store_layout_enabled = true,
    target_max_file_size = '128MB'
);
