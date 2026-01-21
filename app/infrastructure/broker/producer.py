import json
from typing import Self
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.application.interfaces.contracts import BrokerMessage
from ..config.kafka_config import KafkaConfig


class KafkaProducer:
    def __init__(self, config: KafkaConfig):
        self.config = config
        self._producer: AIOKafkaProducer | None = None
        self._started = False

    async def start(self) -> None:
        if self._started:
            return

        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.config.bootstrap_server,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k is not None else None,
        )
        await self._producer.start()
        self._started = True

    async def stop(self) -> None:
        if not self._started or self._producer is None:
            return

        await self._producer.stop()
        self._started = False
        self._producer = None

    async def publish_message(
        self, message: BrokerMessage, key: str | None = None, topic: str | None = None
    ) -> None:
        if not self._started or self._producer is None:
            raise RuntimeError("Producer is not started. Call start() first.")

        target_topic = self.config.default_topic

        try:
            await self._producer.send_and_wait(
                topic=target_topic,
                value=message,
                key=key,
            )
        except KafkaError as e:
            raise RuntimeError(f"Failed to publish message to Kafka: {e}") from e

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
