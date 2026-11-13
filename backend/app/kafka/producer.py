
import os
import json

from datetime import datetime, timezone
from dotenv import load_dotenv
from confluent_kafka import Producer

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
    "client.id": "nexora-retail-producer",
    "acks": "all",
    "enable.idempotence": True,
}

producer = Producer(config)

TOPIC = os.getenv("KAFKA_TOPIC", "retail-events")


def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(
            f"Delivered to {msg.topic()} "
            f"partition={msg.partition()} "
            f"offset={msg.offset()}"
        )


def publish_event(event_type, data):
    event = {
        "event": event_type,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    event_key = (
        data.get("product_id")
        or data.get("order_id")
        or "test"
    )

    producer.produce(
        topic=TOPIC,
        key=str(event_key),
        value=json.dumps(event),
        callback=delivery_report
    )

    remaining = producer.flush(10)

    if remaining:
        raise RuntimeError(
            f"{remaining} messages were not delivered"
        )

    return event


if __name__ == "__main__":
    event = publish_event(
        "order_placed",
        {
            "order_id": 1001,
            "customer_id": 45,
            "items": [
                {
                    "product_id": 10,
                    "quantity": 2
                }
            ]
        }
    )

    print("Published event:")
    print(json.dumps(event, indent=2))

