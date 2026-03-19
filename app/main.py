from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.infrastructure.database import create_engine_from_url, create_session_factory
from app.infrastructure.models import Base
from app.routers.api import router as api_router
from app.routers.web import router as web_router


def create_app(database_url: Optional[str] = None) -> FastAPI:
    settings = get_settings()
    resolved_database_url = database_url or settings.database_url

    engine = create_engine_from_url(resolved_database_url)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        # 意図: import時に副作用を起こさず、アプリ起動時にだけスキーマを整える。
        Base.metadata.create_all(bind=engine)
        yield

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.session_factory = session_factory

    app.include_router(api_router)
    app.include_router(web_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    return app


app = create_app()
