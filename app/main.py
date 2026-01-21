import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from app.infrastructure.ioc_container.container import container
from app.presentation.api.v1.routers.router import router
from app.infrastructure.outbox_worker import (
    OutboxPaymentsWorker,
    OutboxNotificationsWorker,
    OutboxShippingWorker
)
from app.infrastructure.inbox_worker import InboxWorker
from app.presentation.exc_handlers import register_error_handlers


# TODO Move from lifespan to independent worker processes
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with container() as app_container:
        outbox_worker = await app_container.get(OutboxPaymentsWorker)
        inbox_worker = await app_container.get(InboxWorker)
        notifications_worker = await app_container.get(OutboxNotificationsWorker)
        outbox_shipping_worker = await app_container.get(OutboxShippingWorker)


        outbox_task = asyncio.create_task(outbox_worker.run())
        inbox_task = asyncio.create_task(inbox_worker.run())
        notifications_task = asyncio.create_task(notifications_worker.run())
        shipping_task = asyncio.create_task(outbox_shipping_worker.run())

        yield

        outbox_task.cancel()
        inbox_task.cancel()
        notifications_task.cancel()
        shipping_task.cancel()
        try:
            await outbox_task
        except asyncio.CancelledError:
            pass
        try:
            await inbox_task
        except asyncio.CancelledError:
            pass
        try:
            await notifications_task
        except asyncio.CancelledError:
            pass
        try:
            await shipping_task
        except asyncio.CancelledError:
            pass


def create_application() -> FastAPI:
    app = FastAPI(
        root_path="/api",
        description="Orders API service",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    register_error_handlers(app=app)
    setup_dishka(container, app)
    app.include_router(router=router)
    return app


app = create_application()


def start_uvicorn() -> None:
    """Start the Uvicorn server with production configuration."""
    config = uvicorn.Config(
        "app.main:app",
        port=8000,
        loop="uvloop",  # Use uvloop for better performance
        http="httptools",  # Use httptools for better HTTP parsing
    )

    server = uvicorn.Server(config)
    server.run()
