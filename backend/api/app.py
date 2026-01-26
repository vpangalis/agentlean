from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers.cases import router as cases_router
from backend.api.routers.evidence import router as evidence_router


def create_app() -> FastAPI:
    app = FastAPI(title="ValueSims Case API", version="0.1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5500",
            "http://localhost:5500",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(cases_router)
    app.include_router(evidence_router)
    return app


app = create_app()
__all__ = ["create_app"]
