from app.enums import EstadoProspecto
from app.integrations.webhook_service import WebhookService

class AutomationService:

    def __init__(self):

        self.webhook = WebhookService()

    def ejecutar(
        self,
        prospecto,
        estado_anterior: EstadoProspecto,
        estado_nuevo: EstadoProspecto
    ):

        if estado_nuevo == EstadoProspecto.NUEVO:
            self._nuevo(prospecto)

        elif estado_nuevo == EstadoProspecto.CONTACTADO:
            self._contactado(prospecto)

        elif estado_nuevo == EstadoProspecto.INTERESADO:
            self._interesado(prospecto)

        elif estado_nuevo == EstadoProspecto.COTIZADO:
            self._cotizado(prospecto)

        elif estado_nuevo == EstadoProspecto.NEGOCIACION:
            self._negociacion(prospecto)

        elif estado_nuevo == EstadoProspecto.CLIENTE:
            self._cliente(prospecto)

        elif estado_nuevo == EstadoProspecto.DESCARTADO:
            self._descartado(prospecto)


    def _nuevo(self, prospecto):
        pass

    def _contactado(
        self,
        prospecto
    ):

        self.webhook.enviar(

            evento="prospecto.contactado",

            payload={

                "prospecto_id": prospecto.id,

                "empresa": prospecto.nombre_empresa,

                "contacto": prospecto.nombre_contacto,

                "telefono": prospecto.telefono,

                "correo": prospecto.correo,

                "ciudad": prospecto.ciudad,

                "estado": prospecto.estado.value
            }
        )

    def _interesado(self, prospecto):
        pass

    def _cotizado(self, prospecto):
        pass

    def _negociacion(self, prospecto):
        pass

    def _cliente(self, prospecto):
        pass

    def _descartado(self, prospecto):
        pass