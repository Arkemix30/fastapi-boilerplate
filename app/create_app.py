import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin import init_admin
from app.api_router import api_router
from app.core import get_app_settings, get_logger
from app.infrastructure.db import engine

load_dotenv()

logger = get_logger(__name__)


def create_app(**kwargs):
    logger.info("Initializing app...")
    if kwargs.get("test"):
        os.environ["ENVIRONMENT"] = "test"

    app_settings = get_app_settings()

    app = FastAPI(
        title=app_settings.PROJECT_NAME,
    )

    # CORS Related Code
    origins = (
        [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:8080",
        ]
        if kwargs.get("dev") or kwargs.get("test")
        else []
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup():
        logger.info("Starting up...")
        logger.info("Initializing admin...")
        try:
            init_admin(app, engine)
            logger.info("Admin initialized successfully!")

        except Exception as e:
            logger.error(f"Error when initializing admin, error: {e}")
            raise e
        logger.info("Starting up... Done!")

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("Shutting down...")

    # API Related Code
    app.include_router(api_router, prefix=app_settings.API_V1_STR)

    return app
