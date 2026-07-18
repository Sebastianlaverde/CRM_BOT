from fastapi import FastAPI

from app.core.config import settings
from app.routers.health import router as health_router

from app.routers.prospectos import router as prospectos_router

from contextlib import asynccontextmanager

from app.database.base import Base
from app.database.database import engine

# Importar los modelos para que SQLAlchemy los registre
from app.models import Prospecto

from app.routers.historial import router as historial_router

from app.routers.productos import router as productos_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para la plataforma LeadFlow",
    lifespan=lifespan,
)
app.include_router(health_router)
app.include_router(prospectos_router)
app.include_router(historial_router)
app.include_router(productos_router)

@app.get("/", tags=["System"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "status": "running"
    }

