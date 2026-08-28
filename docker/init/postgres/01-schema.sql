CREATE SCHEMA ecommerce;

CREATE TABLE ecommerce."orders"(
    "order_id" UUID NOT NULL,
    "customer_id" UUID NOT NULL,
    "status" TEXT NOT NULL,
    "purchased_at" TIMESTAMPTZ NOT NULL,
    "approved_at" TIMESTAMPTZ NULL,
    "delivered_carrier_at" TIMESTAMPTZ NULL,
    "delivered_customer_at" TIMESTAMPTZ NULL,
    "estimated_delivery_at" TIMESTAMPTZ NULL
);

ALTER TABLE ecommerce."orders"
    ADD PRIMARY KEY("order_id");


CREATE TABLE ecommerce."customers"(
    "customer_id" UUID NOT NULL,
    "customer_unique_id" UUID NOT NULL,
    "zip_code_prefix" INTEGER NOT NULL,
    "city" TEXT NOT NULL,
    "state" VARCHAR(2) NOT NULL
);

ALTER TABLE ecommerce."customers"
    ADD PRIMARY KEY("customer_id");


CREATE TABLE ecommerce."payments"(
    "order_id" UUID NOT NULL,
    "payment_sequential" SMALLINT NOT NULL,
    "type" TEXT NOT NULL,
    "installments" SMALLINT NOT NULL,
    "value" DECIMAL(12, 2) NOT NULL
);

ALTER TABLE ecommerce."payments"
    ADD PRIMARY KEY("order_id", "payment_sequential");


CREATE TABLE ecommerce."reviews"(
    "review_id" UUID NOT NULL,
    "order_id" UUID NOT NULL,
    "score" SMALLINT NOT NULL,
    "comment_title" TEXT NULL,
    "comment_message" TEXT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "answered_at" TIMESTAMPTZ NULL
);

ALTER TABLE ecommerce."reviews"
    ADD PRIMARY KEY("review_id", "order_id");


CREATE TABLE ecommerce."items"(
    "order_id" UUID NOT NULL,
    "item_id" SMALLINT NOT NULL,
    "product_id" UUID NOT NULL,
    "seller_id" UUID NOT NULL,
    "shipping_limit_at" TIMESTAMPTZ NOT NULL,
    "price" DECIMAL(12, 2) NOT NULL,
    "freight_value" DECIMAL(12, 2) NOT NULL
);

ALTER TABLE ecommerce."items"
    ADD PRIMARY KEY("order_id", "item_id");


CREATE TABLE ecommerce."products"(
    "product_id" UUID NOT NULL,
    "category_name" TEXT NULL,
    "name_length" INTEGER NULL,
    "description_length" INTEGER NULL,
    "photos_qty" INTEGER NULL,
    "weight_g" BIGINT NULL,
    "length_cm" INTEGER NULL,
    "height_cm" INTEGER NULL,
    "width_cm" INTEGER NULL
);

ALTER TABLE ecommerce."products"
    ADD PRIMARY KEY("product_id");


CREATE TABLE ecommerce."sellers"(
    "seller_id" UUID NOT NULL,
    "zip_code_prefix" INTEGER NOT NULL,
    "city" TEXT NOT NULL,
    "state" VARCHAR(2) NOT NULL
);

ALTER TABLE ecommerce."sellers"
    ADD PRIMARY KEY("seller_id");


CREATE TABLE ecommerce."geolocation"(
    "geolocation_id" BIGSERIAL NOT NULL,
    "zip_code_prefix" INTEGER NOT NULL,
    "lat" DOUBLE PRECISION NOT NULL,
    "lng" DOUBLE PRECISION NOT NULL,
    "city" TEXT NOT NULL,
    "state" VARCHAR(2) NOT NULL
);

ALTER TABLE ecommerce."geolocation"
    ADD PRIMARY KEY("geolocation_id");


ALTER TABLE ecommerce."items"
    ADD CONSTRAINT "items_order_id_foreign"
    FOREIGN KEY("order_id")
    REFERENCES ecommerce."orders"("order_id");

ALTER TABLE ecommerce."payments"
    ADD CONSTRAINT "payments_order_id_foreign"
    FOREIGN KEY("order_id")
    REFERENCES ecommerce."orders"("order_id");

ALTER TABLE ecommerce."reviews"
    ADD CONSTRAINT "reviews_order_id_foreign"
    FOREIGN KEY("order_id")
    REFERENCES ecommerce."orders"("order_id");

ALTER TABLE ecommerce."items"
    ADD CONSTRAINT "items_product_id_foreign"
    FOREIGN KEY("product_id")
    REFERENCES ecommerce."products"("product_id");

ALTER TABLE ecommerce."items"
    ADD CONSTRAINT "items_seller_id_foreign"
    FOREIGN KEY("seller_id")
    REFERENCES ecommerce."sellers"("seller_id");

ALTER TABLE ecommerce."orders"
    ADD CONSTRAINT "orders_customer_id_foreign"
    FOREIGN KEY("customer_id")
    REFERENCES ecommerce."customers"("customer_id");

ALTER TABLE ecommerce."orders"
    ADD CONSTRAINT "orders_customer_id_unique"
    UNIQUE ("customer_id");