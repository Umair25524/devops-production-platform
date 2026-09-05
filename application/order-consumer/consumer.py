import json
import os
import time

import psycopg
from kafka import KafkaConsumer


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
DATABASE_URL = os.environ["DATABASE_URL"]


def get_db_connection():
    while True:
        try:
            return psycopg.connect(DATABASE_URL)
        except Exception as error:
            print(f"Database connection failed: {error}")
            time.sleep(5)


consumer = KafkaConsumer(
    "orders",
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id="order-consumer-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda value: json.loads(value.decode("utf-8")),
)

print("Order consumer started. Waiting for messages...")

with get_db_connection() as conn:
    for message in consumer:
        order = message.value

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO orders (order_id, customer_id, amount)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (order_id) DO NOTHING
                    """,
                    (
                        order["order_id"],
                        order["customer_id"],
                        order["amount"],
                    ),
                )

            conn.commit()

            print(
                f"Order stored: {order['order_id']} | "
                f"Customer: {order['customer_id']} | "
                f"Amount: {order['amount']}"
            )

        except Exception as error:
            conn.rollback()
            print(f"Failed to store order: {error}")
