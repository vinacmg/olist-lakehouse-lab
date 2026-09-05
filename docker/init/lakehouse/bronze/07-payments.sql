CREATE TABLE IF NOT EXISTS lakehouse.bronze.payments (
    order_id UUID NOT NULL,
    payment_sequential INTEGER NOT NULL,
    type VARCHAR NOT NULL,
    installments INTEGER NOT NULL,
    value DECIMAL(12, 2) NOT NULL,
    cdc_operation VARCHAR NOT NULL,
    cdc_event_at TIMESTAMP(6) WITH TIME ZONE,
    ingested_at TIMESTAMP(6) WITH TIME ZONE NOT NULL
)
COMMENT 'Bronze mirror of ecommerce.payments from PostgreSQL.'
WITH (
    format = 'PARQUET',
    format_version = 3,
    compression_codec = 'SNAPPY',
    object_store_layout_enabled = true,
    target_max_file_size = '128MB'
);
