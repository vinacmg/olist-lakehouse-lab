CREATE TABLE IF NOT EXISTS lakehouse.bronze.products (
    product_id UUID NOT NULL,
    category_name VARCHAR,
    name_length INTEGER,
    description_length INTEGER,
    photos_qty INTEGER,
    weight_g BIGINT,
    length_cm INTEGER,
    height_cm INTEGER,
    width_cm INTEGER,
    ingested_at TIMESTAMP(6) WITH TIME ZONE NOT NULL
)
COMMENT 'Bronze mirror of ecommerce.products from PostgreSQL.'
WITH (
    format = 'PARQUET',
    format_version = 3,
    compression_codec = 'SNAPPY',
    object_store_layout_enabled = true,
    target_max_file_size = '128MB'
);
