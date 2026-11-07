"""Standalone Task 5 API. Only this task is imported and served."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from netflix_ml.shared.io import root
from netflix_ml.tasks.task_05.service import load_forecasting

from netflix_api.dataset import router as dataset_router
from netflix_api.forecasting import router as task_router


def create_app(load_model=True):
    @asynccontextmanager
    async def lifespan(app):
        app.state.forecasting = None
        app.state.active_service = None
        if load_model:
            try:
                value = load_forecasting()
                app.state.forecasting = value
                app.state.active_service = value
            except (OSError, ValueError, KeyError) as exc:
                logging.getLogger(__name__).warning("Artifact unavailable: %s", exc)
        yield

    app = FastAPI(title="Trend Forecasting", version="2.0.0", lifespan=lifespan)
    app.include_router(dataset_router)
    app.include_router(task_router)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "code": "invalid_input",
                "message": "Check input fields",
                "field_errors": [
                    {"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()
                ],
            },
        )

    @app.get("/api/v1/health")
    def health():
        value = app.state.active_service
        return {
            "status": "ok",
            "task_id": 5,
            "artifact_ready": value is not None,
            "task_5_ready": value is not None,
            "run_id": value.metadata["run_id"] if value else None,
        }

    @app.get("/api/v1/tasks")
    def tasks():
        return [
            {
                "id": 5,
                "title": "Trend Forecasting",
                "status": "ready" if app.state.active_service else "not_ready",
            }
        ]

    web = root() / "apps/web/dist"
    if (web / "assets").exists():
        app.mount("/assets", StaticFiles(directory=web / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def frontend(path: str):
            if path.startswith("api/"):
                raise HTTPException(404, detail="Unknown API endpoint")
            requested = (web / path).resolve()
            if requested.is_relative_to(web.resolve()) and requested.is_file():
                return FileResponse(requested)
            return FileResponse(web / "index.html")

    return app


app = create_app()
