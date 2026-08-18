from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy import pool

from app.core.config import settings
from app.database.base import Base

# IMPORTAR TODOS LOS MODELOS
from app.models.prospecto import Prospecto
from app.models.historial_estado import HistorialEstado
from app.models.producto import Producto
from app.models.cotizacion import Cotizacion
from app.models.detalle_cotizacion import DetalleCotizacion
from app.models.estado_cuenta import EstadoCuenta
from app.models.uso_tokens import UsoTokens

config = context.config

# Usar la URL definida en nuestro proyecto
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():

    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():

    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()