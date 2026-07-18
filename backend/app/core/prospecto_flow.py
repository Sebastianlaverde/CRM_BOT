from app.enums import EstadoProspecto


class ProspectoFlow:

    TRANSICIONES_VALIDAS = {

        EstadoProspecto.NUEVO: [
            EstadoProspecto.CONTACTADO,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.CONTACTADO: [
            EstadoProspecto.RESPONDIO,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.RESPONDIO: [
            EstadoProspecto.INTERESADO,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.INTERESADO: [
            EstadoProspecto.COTIZACION_ENVIADA,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.COTIZACION_ENVIADA: [
            EstadoProspecto.NEGOCIACION,
        ],

        EstadoProspecto.NEGOCIACION: [
            EstadoProspecto.CLIENTE,
            EstadoProspecto.DESCARTADO,
        ],

        EstadoProspecto.CLIENTE: [],

        EstadoProspecto.DESCARTADO: [],
    }

    @classmethod
    def puede_cambiar(
        cls,
        actual: EstadoProspecto,
        nuevo: EstadoProspecto
    ) -> bool:

        return nuevo in cls.TRANSICIONES_VALIDAS.get(actual, [])