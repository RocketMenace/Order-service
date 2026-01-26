import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.infrastructure.ioc_container.container import container
from app.presentation.api.v1.routers.router import router
from app.presentation.exc_handlers import register_error_handlers


def create_application() -> FastAPI:
    app = FastAPI(
        root_path="/api",
        description="Orders API service",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
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
