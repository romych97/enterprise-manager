from kafka import KafkaProducer, KafkaConsumer
import json
from typing import Any, Dict
import os


class KafkaManager:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def produce_event(self, topic: str, event: Dict[str, Any]):
        """Produce an event to a Kafka topic"""
        try:
            self.producer.send(topic, event)
            self.producer.flush()
        except Exception as e:
            print(f"Error producing event: {e}")

    def create_consumer(self, topic: str, group_id: str):
        """Create a Kafka consumer for a specific topic"""
        return KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )


# Initialize Kafka manager
kafka_manager = KafkaManager()

# Event topics
TOPICS = {
    "USER_ACTIVITY": "user_activity",
    "ORDER_STATUS_CHANGE": "order_status_change",
    "TASK_ASSIGNMENT": "task_assignment",
    "NOTIFICATION": "notification",
}
