import logging
from datetime import datetime
from datetime import timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.enums import EstadoProspecto
from app.integrations.whatsapp_service import WhatsAppService
from app.repositories.prospecto_repository import ProspectoRepository
from app.services.estado_cuenta_service import EstadoCuentaService
from app.services.evento_service import EventoService
from app.services.prospecto_service import ProspectoService
from app.utils.horario_laboral import es_horario_laboral
from app.schemas.primer_contacto import (
    PrimerContactoResultado,
    PrimerContactoEjecutarResponse,
)

logger = logging.getLogger(__name__)

# Sin variable de entorno a propósito -- a diferencia del tope de
# embudo, este no lo pidieron configurable. Mismo patrón que
# UMBRAL_DIAS_POR_ESTADO en SeguimientoService.
MAXIMO_CONTACTOS_DIA = 10

MAX_INTENTOS_PRIMER_CONTACTO = 3

ESTADOS_EN_PROCESO = [

    EstadoProspecto.CONTACTADO,

    EstadoProspecto.RESPONDIO,

    EstadoProspecto.INTERESADO,

    EstadoProspecto.COTIZADO,

    EstadoProspecto.NEGOCIACION,

]

# Pendiente de aprobación en Meta -- ver PROJECT_STATUS.md.
NOMBRE_PLANTILLA_PRIMER_CONTACTO = "primer_contacto_negocio"


class PrimerContactoService:

    def __init__(self, db: Session):

        self.db = db

        self.prospecto_repository = ProspectoRepository(db)

        self.prospecto_service = ProspectoService(db)

        self.evento_service = EventoService(db)

        self.estado_cuenta_service = EstadoCuentaService(db)

        self.whatsapp = WhatsAppService()

    def ejecutar(
        self,
        dry_run: bool = True
    ) -> PrimerContactoEjecutarResponse:

        if not es_horario_laboral():

            return self._respuesta_vacia(
                dry_run,
                "Fuera de horario laboral (lun-vie 9am-5pm Bogotá)."
            )

        if self.estado_cuenta_service.esta_pausada_prospeccion():

            return self._respuesta_vacia(
                dry_run,
                "Prospección pausada por el cliente."
            )

        en_proceso = self.prospecto_repository.contar_por_estados(
            ESTADOS_EN_PROCESO
        )

        if en_proceso >= settings.TOPE_EMBUDO_ACTIVO:

            return self._respuesta_vacia(
                dry_run,
                f"Tope de embudo activo alcanzado "
                f"({en_proceso}/{settings.TOPE_EMBUDO_ACTIVO})."
            )

        enviados_hoy = self._contar_enviados_hoy()

        cupo_restante = MAXIMO_CONTACTOS_DIA - enviados_hoy

        if cupo_restante <= 0:

            return self._respuesta_vacia(
                dry_run,
                f"Tope diario ya alcanzado "
                f"({enviados_hoy}/{MAXIMO_CONTACTOS_DIA})."
            )

        candidatos = self._buscar_candidatos(
            cupo_restante
        )

        resultados = [

            self._procesar(
                prospecto,
                dry_run
            )

            for prospecto in candidatos

        ]

        enviados = sum(

            1
            for resultado in resultados
            if resultado.estado_resultado == "enviado"

        )

        return PrimerContactoEjecutarResponse(

            dry_run=dry_run,

            evaluados=len(resultados),

            enviados=enviados,

            motivo_corte=None,

            resultados=resultados

        )

    def _respuesta_vacia(
        self,
        dry_run: bool,
        motivo: str
    ) -> PrimerContactoEjecutarResponse:

        return PrimerContactoEjecutarResponse(

            dry_run=dry_run,

            evaluados=0,

            enviados=0,

            motivo_corte=motivo,

            resultados=[]

        )

    def _contar_enviados_hoy(self) -> int:

        inicio_de_hoy = (
            datetime.now(timezone.utc)
            .replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
        )

        return (
            self.evento_service
            .contar_primer_contacto_enviado_desde(
                inicio_de_hoy
            )
        )

    def _buscar_candidatos(
        self,
        cupo_restante: int
    ):

        candidatos = []

        prospectos_nuevos = (
            self.prospecto_repository
            .listar_por_estado_ordenado(
                EstadoProspecto.NUEVO
            )
        )

        for prospecto in prospectos_nuevos:

            intentos_fallidos = (
                self.evento_service
                .contar_primer_contacto_fallido_de_prospecto(
                    prospecto.id
                )
            )

            if intentos_fallidos >= MAX_INTENTOS_PRIMER_CONTACTO:
                continue

            candidatos.append(
                prospecto
            )

            if len(candidatos) >= cupo_restante:
                break

        return candidatos

    def _procesar(
        self,
        prospecto,
        dry_run: bool
    ) -> PrimerContactoResultado:

        if dry_run:

            return PrimerContactoResultado(

                prospecto_id=prospecto.id,

                nombre_empresa=prospecto.nombre_empresa,

                telefono=prospecto.telefono,

                estado_resultado="pendiente_enviar"

            )

        resultado_envio = self.whatsapp.enviar_plantilla(

            telefono=prospecto.telefono,

            nombre_plantilla=NOMBRE_PLANTILLA_PRIMER_CONTACTO,

            variables=[prospecto.nombre_empresa]

        )

        if not resultado_envio["exitoso"]:

            self.evento_service.registrar_primer_contacto_fallido(
                prospecto,
                resultado_envio["detalle"]
            )

            self.db.commit()

            return PrimerContactoResultado(

                prospecto_id=prospecto.id,

                nombre_empresa=prospecto.nombre_empresa,

                telefono=prospecto.telefono,

                estado_resultado="fallido"

            )

        self.prospecto_service.cambiar_estado(

            prospecto_id=prospecto.id,

            estado=EstadoProspecto.CONTACTADO,

            observacion=(
                f"Se envió primer contacto por WhatsApp "
                f"(plantilla {NOMBRE_PLANTILLA_PRIMER_CONTACTO})."
            )

        )

        self.evento_service.registrar_primer_contacto_enviado(
            prospecto
        )

        self.db.commit()

        return PrimerContactoResultado(

            prospecto_id=prospecto.id,

            nombre_empresa=prospecto.nombre_empresa,

            telefono=prospecto.telefono,

            estado_resultado="enviado"

        )
