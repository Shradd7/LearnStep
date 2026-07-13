import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from classpath import __version__
from classpath.api.demo import router as demo_router
from classpath.api.health import router as health_router
from classpath.core.config import Settings, get_settings
from classpath.db.session import get_session_factory
from classpath.repositories.demo import purge_expired_documents


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or get_settings()

    async def cleanup_worker() -> None:
        while True:

            def cleanup_once() -> None:
                with get_session_factory(active_settings.database_url)() as session:
                    purge_expired_documents(
                        session, storage_root=Path(active_settings.private_data_root)
                    )

            await asyncio.to_thread(cleanup_once)
            await asyncio.sleep(60)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        task = asyncio.create_task(cleanup_worker()) if active_settings.app_env != "test" else None
        yield
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    application = FastAPI(
        title=active_settings.app_name,
        version=__version__,
        debug=active_settings.app_debug,
        description=(
            "Controlled LearnStep portfolio demo. All examples and seeded concepts are "
            "explicitly synthetic."
        ),
        lifespan=lifespan,
    )
    application.state.settings = active_settings
    application.dependency_overrides[get_settings] = lambda: active_settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Accept", "Authorization", "Content-Type"],
    )
    application.include_router(health_router)
    application.include_router(demo_router)
    return application


app = create_app()
