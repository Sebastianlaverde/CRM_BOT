class RuleEngine:

    def evaluate(
        self,
        contexto: dict,
        mensaje: str
    ):

        reglas = []

        reglas.append(
            "Nunca inventes información."
        )

        reglas.append(
            "Nunca cambies precios."
        )

        reglas.append(
            "Nunca prometas fechas de entrega."
        )

        reglas.append(
            "Nunca aceptes pagos."
        )

        reglas.append(
            "Si no conoces la respuesta, solicita ayuda a un asesor."
        )

        reglas.extend(
            self._reglas_por_estado(contexto)
        )

        return reglas

    def _reglas_por_estado(
        self,
        contexto: dict
    ):

        from app.enums import EstadoProspecto

        prospecto = contexto["prospecto"]

        estado = prospecto.estado

        reglas = []

        if estado == EstadoProspecto.RESPONDIO:

            reglas.append(
                "Actualiza el estado a INTERESADO SOLO si el cliente muestra "
                "al menos UNA de estas señales concretas: (a) pregunta el "
                "precio de un producto específico, (b) menciona una cantidad "
                "o volumen que necesita, (c) describe una necesidad propia de "
                "su negocio (ej. 'necesito [producto] para mi negocio'), o "
                "(d) pide explícitamente una cotización. "
                "NO actualices el estado si el cliente solo pregunta sobre la "
                "empresa (quién eres, hace cuánto existen), sobre el catálogo "
                "en general sin especificar su necesidad (ej. '¿qué productos "
                "manejan?', '¿solo hacen esto o también otras cosas?'), o "
                "hace conversación genérica sin señales de intención de compra. "
                "Ante la duda, NO actualices el estado — es mejor esperar una "
                "señal más clara en el siguiente mensaje que marcar interés "
                "de forma prematura."
            )

        if estado == EstadoProspecto.INTERESADO:

            reglas.append(
                "Solo crea una cotización formal (gestionar_cotizacion) "
                "cuando tengas confirmados los productos y cantidades "
                "exactas que el cliente quiere. No la crees si aún "
                "faltan datos."
            )

            reglas.append(
                "Después de crear una cotización exitosamente, "
                "actualiza el estado del prospecto a COTIZADO usando "
                "actualizar_estado, en el mismo turno."
            )

        if estado == EstadoProspecto.COTIZADO:

            reglas.append(
                "Si el cliente empieza a negociar la cotización "
                "(pide descuento, cambia cantidades, discute "
                "condiciones), actualiza su estado a NEGOCIACION "
                "usando actualizar_estado."
            )

        if estado == EstadoProspecto.NEGOCIACION:

            reglas.append(
                "Solo actualiza el estado a CLIENTE cuando el "
                "cliente confirme explícitamente que quiere "
                "proceder con la compra. No lo hagas por señales "
                "ambiguas."
            )

        if estado not in (
            EstadoProspecto.CLIENTE,
            EstadoProspecto.DESCARTADO
        ):

            reglas.append(
                "Si el cliente indica explícitamente que ya no "
                "le interesa o quiere terminar la conversación, "
                "actualiza su estado a DESCARTADO usando "
                "actualizar_estado."
            )

        return reglas