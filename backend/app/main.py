from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.database.base import Base
from app.database.database import engine

# Registrar todos los modelos
from app import models

from app.routers.health import router as health_router
from app.routers.prospectos import router as prospectos_router
from app.routers.historial import router as historial_router
from app.routers.productos import router as productos_router
from app.routers.cotizaciones import router as cotizaciones_router
from app.routers.eventos import router as eventos_router
from app.routers.conversacion import router as conversacion_router
from app.routers.sourcing import router as sourcing_router

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
app.include_router(cotizaciones_router)
app.include_router(eventos_router)
app.include_router(conversacion_router)
app.include_router(sourcing_router)

@app.get("/", tags=["System"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "status": "running",
    }