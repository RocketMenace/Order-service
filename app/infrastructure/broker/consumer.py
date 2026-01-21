import asyncio
import json
from typing import Optional
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from aiokafka.structs import ConsumerRecord

from ..config.kafka_config import KafkaConfig


class KafkaConsumer:
    def __init__(self, config: KafkaConfig, consumer_group_id: str = "order-service-group"):
        self.config = config
        self.consumer_group_id = consumer_group_id
        self._consumer: AIOKafkaConsumer | None = None
        self._started = False

    async def start(self) -> None:
        if self._started:
            return

        if not self.config.bootstrap_server:
            raise ValueError(
                "Kafka bootstrap server is not configured. "
                "Please set KAFKA_BOOTSTRAP environment variable (e.g., 'kafka:9092' for Docker or 'localhost:29092' for local)."
            )

        self._consumer = AIOKafkaConsumer(
            self.config.default_topic,
            bootstrap_servers=self.config.bootstrap_server,
            group_id=self.consumer_group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None,
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )
        await self._consumer.start()
        self._started = True

    async def stop(self) -> None:
        if not self._started or self._consumer is None:
            return

        await self._consumer.stop()
        self._started = False
        self._consumer = None

    async def consume_message(self) -> Optional[ConsumerRecord]:
        if not self._started or self._consumer is None:
            raise RuntimeError("Consumer is not started. Call start() first.")

        try:
            async for message in self._consumer:
                return message
        finally:
            await self._consumer.stop()

