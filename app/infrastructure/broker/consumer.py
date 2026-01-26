import json
from typing import Optional

from aiokafka import AIOKafkaConsumer
from aiokafka.structs import ConsumerRecord

from app.application.use_cases.shipping_response import ShippingResponseUseCase
from app.infrastructure.config.kafka_config import KafkaConfig
from app.infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class KafkaConsumer:
    def __init__(self, config: KafkaConfig, use_case: ShippingResponseUseCase):
        self.config = config
        self._consumer: AIOKafkaConsumer | None = None
        self._started = False
        self.consumer_group_id = "order-service-group"
        self.use_case = use_case

    async def start(self) -> None:
        if self._started:
            return

        self._consumer = AIOKafkaConsumer(
            self.config.default_topic,
            bootstrap_servers=self.config.bootstrap_server,
            group_id=self.consumer_group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None,
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            auto_offset_reset="earliest",
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
                try:
                    logger.info(
                        "Process message",
                        partition=message.partition,
                        data=message.value,
                    )
                    await self.use_case(message=message.value)
                    await self._consumer.commit()
                except Exception as e:
                    logger.error(
                        "Failed to process message", data=message.value, error=str(e)
                    )
                    raise
        finally:
            await self._consumer.stop()
