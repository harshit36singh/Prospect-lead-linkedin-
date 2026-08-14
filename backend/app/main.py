from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import health, icps, pipeline

app = FastAPI(title="Prospect Lead API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(icps.router)
app.include_router(pipeline.router)


@app.on_event("startup")
def on_startup() -> None:
    import app.models  # noqa: F401  (ensure all models are registered before create_all)

    Base.metadata.create_all(bind=engine)
