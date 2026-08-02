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

        return reglas