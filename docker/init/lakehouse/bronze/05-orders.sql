CREATE TABLE IF NOT EXISTS lakehouse.bronze.orders (
    order_id UUID NOT NULL,
    customer_id UUID NOT NULL,
    status VARCHAR NOT NULL,
    purchased_at TIMESTAMP(6) WITH TIME ZONE NOT NULL,
    approved_at TIMESTAMP(6) WITH TIME ZONE,
    delivered_carrier_at TIMESTAMP(6) WITH TIME ZONE,
    delivered_customer_at TIMESTAMP(6) WITH TIME ZONE,
    estimated_delivery_at TIMESTAMP(6) WITH TIME ZONE,
    cdc_operation VARCHAR NOT NULL,
    cdc_event_at TIMESTAMP(6) WITH TIME ZONE,
    ingested_at TIMESTAMP(6) WITH TIME ZONE NOT NULL
)
COMMENT 'Bronze mirror of ecommerce.orders from PostgreSQL.'
WITH (
    format = 'PARQUET',
    format_version = 3,
    compression_codec = 'SNAPPY',
    object_store_layout_enabled = true,
    target_max_file_size = '128MB'
);
