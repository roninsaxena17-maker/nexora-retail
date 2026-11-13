
import os
import json

from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaException

from app.search.opensearch_client import client

load_dotenv()

config = {
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "SCRAM-SHA-256",
    "sasl.username": os.getenv("KAFKA_USERNAME"),
    "sasl.password": os.getenv("KAFKA_PASSWORD"),
    "ssl.ca.location": os.path.abspath(
        os.getenv("KAFKA_CA_LOCATION")
    ),
    "group.id": "nexora-retail-product-sync-v1",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
}

TOPIC = os.getenv("KAFKA_TOPIC", "retail-events")
INDEX_NAME = "nexora-products"


def sync_product(data):
    product_id = data["product_id"]

    document = {
        "product_id": product_id,
        "name": data["name"],
        "description": data.get("description"),
        "price": data["price"],
        "image_url": data.get("image_url"),
        "stock_quantity": data["stock_quantity"],
        "category": data.get("category"),
        "city": data.get("city")
    }

    client.index(
        index=INDEX_NAME,
        id=str(product_id),
        body=document,
        refresh="wait_for"
    )

    print(f"OpenSearch synced product ID: {product_id}")


def process_event(event):
    event_type = event.get("event")
    data = event.get("data", {})

    if event_type in (
        "product_created",
        "product_updated",
        "inventory_updated"
    ):
        sync_product(data)

    else:
        print(f"Ignoring unsupported event: {event_type}")


def main():
    consumer = Consumer(config)
    consumer.subscribe([TOPIC])

    print(f"Listening on topic: {TOPIC}")
    print("Product and inventory synchronization is active.")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                raise KafkaException(msg.error())

            event = json.loads(msg.value().decode("utf-8"))

            print("\n========== KAFKA EVENT ==========")
            print(json.dumps(event, indent=2))

            process_event(event)

            consumer.commit(
                message=msg,
                asynchronous=False
            )

            print("Event processed and offset committed.")
            print("=================================")

    except KeyboardInterrupt:
        print("\nConsumer stopped.")

    finally:
        consumer.close()


if __name__ == "__main__":
    main()

