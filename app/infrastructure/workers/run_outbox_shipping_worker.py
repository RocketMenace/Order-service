import asyncio
import sys

from app.infrastructure.config.logging import get_logger
from app.infrastructure.workers.container import create_workers_container
from app.infrastructure.workers.outbox_worker import OutboxShippingWorker

logger = get_logger(__name__)


async def main():
    container = create_workers_container()

    async with container() as request_container:
        worker: OutboxShippingWorker = await request_container.get(OutboxShippingWorker)

        try:
            await worker.run()
        except KeyboardInterrupt:
            logger.info("Stopping OutboxShippingWorker")
        except Exception as e:
            logger.warning("Error in OutboxShippingWorker", error=str(e))
            raise
        finally:
            logger.info("OutboxShippingWorker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Failed to start worker: {e}")
        logger.error("Failed to start worker", error=str(e))
        sys.exit(1)



