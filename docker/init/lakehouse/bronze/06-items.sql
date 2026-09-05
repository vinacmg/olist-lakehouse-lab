CREATE TABLE IF NOT EXISTS lakehouse.bronze.items (
    order_id UUID NOT NULL,
    item_id INTEGER NOT NULL,
    product_id UUID NOT NULL,
    seller_id UUID NOT NULL,
    shipping_limit_at TIMESTAMP(6) WITH TIME ZONE NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    freight_value DECIMAL(12, 2) NOT NULL,
    cdc_operation VARCHAR NOT NULL,
    cdc_event_at TIMESTAMP(6) WITH TIME ZONE,
    ingested_at TIMESTAMP(6) WITH TIME ZONE NOT NULL
)
COMMENT 'Bronze mirror of ecommerce.items from PostgreSQL.'
WITH (
    format = 'PARQUET',
    format_version = 3,
    compression_codec = 'SNAPPY',
    object_store_layout_enabled = true,
    target_max_file_size = '128MB'
);
