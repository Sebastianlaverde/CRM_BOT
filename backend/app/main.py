from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
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
from app.routers.seguimiento import router as seguimiento_router
from app.routers.primer_contacto import router as primer_contacto_router
from app.routers.interno import router as interno_router
from app.services.estado_cuenta_poller import verificar_estado_cuenta_periodico
from app.services.uso_tokens_reporter import reportar_uso_tokens_periodico
from app.services.estadisticas_reporter import reportar_estadisticas_periodico

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    # Red de seguridad del campo `activo` -- ver LeadFlow Control.
    # No depende de n8n a propósito: es un mecanismo de disponibilidad,
    # no lógica de negocio, y no debería fallar junto con la misma
    # infraestructura que intenta cubrir.
    scheduler.add_job(
        verificar_estado_cuenta_periodico,
        "interval",
        minutes=3,
        id="verificar_estado_cuenta"
    )

    # Sin urgencia (a diferencia de arriba) -- una vez al día alcanza.
    scheduler.add_job(
        reportar_uso_tokens_periodico,
        "interval",
        days=1,
        id="reportar_uso_tokens"
    )

    scheduler.add_job(
        reportar_estadisticas_periodico,
        "interval",
        days=1,
        id="reportar_estadisticas"
    )

    scheduler.start()

    yield

    scheduler.shutdown()


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
app.include_router(seguimiento_router)
app.include_router(primer_contacto_router)
app.include_router(interno_router)

@app.get("/", tags=["System"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "status": "running",
    }