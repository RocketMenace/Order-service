import asyncio
import sys

from app.infrastructure.broker.consumer import KafkaConsumer
from app.infrastructure.config.logging import get_logger
from app.infrastructure.workers.container import create_workers_container

logger = get_logger(__name__)


async def main():
    container = create_workers_container()
    async with container() as container:
        consumer = await container.get(KafkaConsumer)

        try:
            await consumer.start()
            await consumer.consume_message()
        except KeyboardInterrupt:
            logger.info("Stopping KafkaConsumer")
        except Exception as e:
            logger.warning("Error in KafkaConsumer", error=str(e))
            raise
        finally:
            logger.info("KafkaConsumer stopped stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error("Failed to start KafkaConsumer", error=str(e))
        sys.exit(1)
