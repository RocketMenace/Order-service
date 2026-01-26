import asyncio
import sys

from app.infrastructure.config.logging import get_logger
from app.infrastructure.workers.container import create_workers_container
from app.infrastructure.workers.inbox_worker import InboxWorker

logger = get_logger(__name__)


async def main():
    container = create_workers_container()

    async with container() as request_container:
        worker: InboxWorker = await request_container.get(InboxWorker)

        try:
            await worker.run()
        except KeyboardInterrupt:
            logger.info("Stopping InboxWorker")
        except Exception as e:
            logger.warning("Error in InboxWorker", error=str(e))
            raise
        finally:
            logger.info("InboxWorker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error("Failed to start worker", error=str(e))
        sys.exit(1)
