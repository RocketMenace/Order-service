import json
from typing import Self

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.application.interfaces.contracts import BrokerMessageRequest
from app.infrastructure.config.kafka_config import KafkaConfig
from app.infrastructure.config.logging import get_logger

logger = get_logger(__name__)


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
            enable_idempotence=True,
            acks=1,
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
        self,
        message: BrokerMessageRequest,
        key: str | None = None,
        topic: str | None = None,
    ) -> None:
        if not self._started or self._producer is None:
            raise RuntimeError("Producer is not started. Call start() first.")

        target_topic = self.config.default_topic

        try:
            logger.info("Push message: ", data=message)
            await self._producer.send_and_wait(
                topic=target_topic,
                value=message,
                key=key,
            )
        except KafkaError as e:
            logger.error("Failed to publish message to Kafka: ", error=str(e))
            raise RuntimeError(f"Failed to publish message to Kafka: {e}") from e

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.stop()
