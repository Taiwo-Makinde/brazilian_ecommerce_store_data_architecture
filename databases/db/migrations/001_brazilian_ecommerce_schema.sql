CREATE TABLE IF NOT EXISTS geolocation (														
			geolocation_zip_code_prefix VARCHAR (5),
			geolocation_lat NUMERIC (17, 14),
			geolocation_lng NUMERIC (17, 14),
			geolocation_city TEXT, 
			geolocation_state VARCHAR(2)
			);

CREATE TABLE IF NOT EXISTS customer (
			customer_id VARCHAR(32) PRIMARY KEY, 
			customer_unique_id VARCHAR,
			customer_zip_code_prefix VARCHAR,
			customer_city TEXT,
			customer_state VARCHAR
			);

CREATE TABLE IF NOT EXISTS sellers (
			seller_id VARCHAR (32) PRIMARY KEY,
			seller_zip_prefix VARCHAR (5), 
			seller_city TEXT,
			seller_state VARCHAR (2)
			);

CREATE TABLE IF NOT EXISTS orders(
			order_id VARCHAR (32) PRIMARY KEY,
			customer_id VARCHAR references customer (customer_id) ON DELETE RESTRICT,
			order_status VARCHAR,
			order_purchase_timestamp TEXT, 																	--We would transform order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, and order_estimated_delivery_date columns to timestamp using the to_timestamp 
			order_approved_at TEXT,
			order_delivered_carrier_date TEXT,
			order_delivered_customer_date TEXT,
			order_estimated_delivery_date TEXT
			);

CREATE TABLE IF NOT EXISTS products (
			product_id VARCHAR PRIMARY KEY,
			product_category_name TEXT,
			product_name_length INT,
			product_description_length INT,
			product_photos_qty INT, 
			product_weight_g INT, 
			product_length_cm INT,
			product_height_cm INT, 
			product_width_cm, INT
			);

CREATE TABLE IF NOT EXISTS order_reviews (
			review_id VARCHAR,
			order_id VARCHAR REFERENCES orders(order_id) ON DELETE RESTRICT,
			review_score INT, 
			review_comment_title TEXT, 
			review_comment_message TEXT, 
			review_creation_date TEXT, 														--We would transform review_creation_date and review_answer_timestamp columns to timestamp using the to_timestamp
			review_answer_timestamp TEXT,
			PRIMARY KEY (review_id, order_id)			
			);

CREATE TABLE IF NOT EXISTS order_payments (
			order_id VARCHAR REFERENCES orders(order_id) ON DELETE RESTRICT,
			payment_sequential INT,
			payment_type TEXT,
			payment_installments INT, 
			payment_value NUMERIC (17, 14),
			PRIMARY KEY (order_id, payment_sequential)
			);

CREATE TABLE IF NOT EXISTS order_items (
			order_id VARCHAR REFERENCES orders(order_id) ON DELETE RESTRICT,
			order_item_id VARCHAR PRIMARY KEY,
			product_id VARCHAR REFERENCES products(product_id) ON DELETE RESTRICT,
			seller_id VARCHAR REFERENCES sellers(seller_id) ON DELETE RESTRICT,
			shipping_limit_date TEXT,																		-- --We would transform shipping_limit_date column to timestamp using the to_timestamp
			price NUMERIC (17, 14),
			freight_value NUMERIC (17, 14),
			PRIMARY KEY (order_id, order_item_id)
			);
			
CREATE TABLE IF NOT EXISTS product_category_name_translation (
			product_category_name TEXT,
			product_category_name_english TEXT
			);