from datetime import datetime
from datetime import timezone

from sqlalchemy.orm import Session

from app.enums import (
    AutorMensaje,
    TipoMensaje,
    EstadoProspecto,
)
from app.models.mensaje import Mensaje
from app.repositories.sesion_repository import SesionRepository
from app.repositories.mensaje_repository import MensajeRepository
from app.services.evento_service import EventoService
from app.services.decision_action_executor import DecisionActionExecutor
from app.integrations.webhook_service import WebhookService
from app.agents.agent_factory import AgentFactory
from app.schemas.seguimiento import (
    SeguimientoResultado,
    SeguimientoEjecutarResponse,
)

UMBRAL_DIAS_POR_ESTADO = {

    EstadoProspecto.CONTACTADO: 3,

    EstadoProspecto.RESPONDIO: 2,

    EstadoProspecto.INTERESADO: 2,

    EstadoProspecto.COTIZADO: 3,

    EstadoProspecto.NEGOCIACION: 2,

}

# Ventana de servicio al cliente de WhatsApp Business API: fuera de
# esto, un mensaje saliente iniciado por nosotros debe ser una
# plantilla pre-aprobada por Meta, no texto libre generado por la IA.
VENTANA_SERVICIO_HORAS = 24

# Pendiente de aprobación en Meta Business Manager. Única plantilla
# de seguimiento por ahora (sirve para INTERESADO y COTIZADO sin
# mencionar montos) — si más adelante se aprueban plantillas
# distintas por estado, esto pasa a ser un dict por EstadoProspecto
# como UMBRAL_DIAS_POR_ESTADO.
NOMBRE_PLANTILLA_SEGUIMIENTO = "seguimiento_cotizacion_pizza"


class SeguimientoService:

    def __init__(self, db: Session):

        self.db = db

        self.sesion_repository = SesionRepository(db)

        self.mensaje_repository = MensajeRepository(db)

        self.evento_service = EventoService(db)

        self.action_executor = DecisionActionExecutor(db)

        self.webhook = WebhookService()

        self.agent = AgentFactory.get_agent(
            "commercial",
            db
        )

    def ejecutar(
        self,
        dry_run: bool = True
    ) -> SeguimientoEjecutarResponse:

        candidatos = self._buscar_candidatos()

        resultados = [

            self._procesar(
                sesion,
                dias_sin_respuesta,
                dry_run
            )

            for sesion, dias_sin_respuesta in candidatos

        ]

        enviados = sum(

            1
            for resultado in resultados
            if resultado.estado_resultado == "enviado"

        )

        return SeguimientoEjecutarResponse(

            dry_run=dry_run,

            evaluados=len(resultados),

            enviados=enviados,

            resultados=resultados

        )

    def _buscar_candidatos(self):

        ahora = datetime.now(timezone.utc)

        candidatos = []

        for sesion in self.sesion_repository.listar_esperando_cliente():

            umbral = UMBRAL_DIAS_POR_ESTADO.get(
                sesion.prospecto.estado
            )

            if umbral is None:
                continue

            dias_sin_respuesta = (
                ahora - sesion.ultima_actividad
            ).days

            if dias_sin_respuesta < umbral:
                continue

            candidatos.append((
                sesion,
                dias_sin_respuesta
            ))

        return candidatos

    def _procesar(
        self,
        sesion,
        dias_sin_respuesta,
        dry_run
    ):

        prospecto = sesion.prospecto

        horas_desde_cliente = (
            self._horas_desde_ultimo_mensaje_cliente(
                sesion.id
            )
        )

        if horas_desde_cliente < VENTANA_SERVICIO_HORAS:

            canal_envio = "texto_libre"

            plantilla = None

            decision = self.agent.generar_seguimiento(
                prospecto.id,
                sesion.canal,
                dias_sin_respuesta
            )

            contenido = decision["contenido"]

            acciones = decision["acciones"]

        else:

            canal_envio = "plantilla"

            plantilla = NOMBRE_PLANTILLA_SEGUIMIENTO

            contenido = self._renderizar_plantilla_seguimiento(
                prospecto
            )

            acciones = []

        if dry_run:

            return SeguimientoResultado(

                prospecto_id=prospecto.id,

                nombre_empresa=prospecto.nombre_empresa,

                dias_sin_respuesta=dias_sin_respuesta,

                mensaje=contenido,

                canal_envio=canal_envio,

                plantilla=plantilla,

                estado_resultado="pendiente_enviar"

            )

        self.action_executor.ejecutar(
            acciones,
            prospecto
        )

        mensaje = Mensaje(

            sesion_id=sesion.id,

            autor=AutorMensaje.IA,

            tipo=TipoMensaje.TEXTO,

            contenido=contenido

        )

        self.mensaje_repository.create(
            mensaje
        )

        sesion.ultima_actividad = datetime.now(
            timezone.utc
        )

        self.db.commit()

        self.evento_service.registrar_seguimiento_enviado(
            prospecto,
            dias_sin_respuesta
        )

        self.db.commit()

        self.webhook.enviar(

            evento="prospecto.seguimiento",

            payload={

                "prospecto_id": prospecto.id,

                "empresa": prospecto.nombre_empresa,

                "contacto": prospecto.nombre_contacto,

                "telefono": prospecto.telefono,

                "correo": prospecto.correo,

                "ciudad": prospecto.ciudad,

                "estado": prospecto.estado.value,

                "dias_sin_respuesta": dias_sin_respuesta,

                "mensaje": contenido

            }

        )

        return SeguimientoResultado(

            prospecto_id=prospecto.id,

            nombre_empresa=prospecto.nombre_empresa,

            dias_sin_respuesta=dias_sin_respuesta,

            mensaje=contenido,

            canal_envio=canal_envio,

            plantilla=plantilla,

            estado_resultado="enviado"

        )

    def _horas_desde_ultimo_mensaje_cliente(
        self,
        sesion_id
    ) -> float:

        ultimo_mensaje_cliente = (
            self.mensaje_repository
            .obtener_ultimo_mensaje_cliente(
                sesion_id
            )
        )

        if ultimo_mensaje_cliente is None:

            # No debería pasar (ESPERANDO_CLIENTE implica que hubo
            # al menos un mensaje del cliente), pero si pasa, es más
            # seguro asumir la ventana cerrada (usar plantilla) que
            # arriesgar texto libre fuera de ventana.
            return float("inf")

        ahora = datetime.now(timezone.utc)

        return (

            ahora - ultimo_mensaje_cliente.created_at

        ).total_seconds() / 3600

    def _renderizar_plantilla_seguimiento(
        self,
        prospecto
    ) -> str:

        nombre = (
            prospecto.nombre_contacto
            or prospecto.nombre_empresa
        )

        return (

            f"Hola {nombre}, ¿cómo vas? 👋\n\n"

            f"Seguimos atentos para ayudarte con tus cajas para "
            f"pizza. Si todavía te interesa, escríbenos y retomamos "
            f"la cotización de una vez.\n\n"

            f"Si ya no lo necesitas, no hay problema, solo "
            f"respóndenos para cerrar el tema.\n\n"

            f"Si prefieres no recibir más mensajes nuestros, "
            f"responde BAJA."

        )
