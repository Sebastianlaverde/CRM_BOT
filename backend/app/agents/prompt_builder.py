class PromptBuilder:

    def build(
        self,
        contexto: dict,
        reglas: list[str],
        objetivo: str,
        tools: list[dict]
    ):

        prospecto = contexto["prospecto"]

        prompt = f"""


    Eres un asesor comercial experto de la empresa.

    =========================
    OBJETIVO
    ========

    {objetivo}

    =========================
    INFORMACIÓN DEL CLIENTE
    =======================

    Empresa: {prospecto.nombre_empresa}

    Contacto: {prospecto.nombre_contacto or "No registrado"}

    Ciudad: {prospecto.ciudad}

    Estado comercial: {prospecto.estado.value}

    =========================
    REGLAS
    ======

    """


        for regla in reglas:
            prompt += f"- {regla}\n"

        prompt += """
    ```

    =========================
    HERRAMIENTAS DISPONIBLES
    ========================

    """


        for tool in tools:

            prompt += (
                f"- {tool['name']}\n"
                f"  Descripción: {tool['description']}\n"
            )

            parameters = tool.get("parameters")

            if parameters:

                prompt += (
                    "  Parámetros disponibles:\n"
                )

                properties = parameters.get(
                    "properties",
                    {}
                )

                required = parameters.get(
                    "required",
                    []
                )

                for parametro, info in properties.items():

                    requerido = (
                        "Sí"
                        if parametro in required
                        else "No"
                    )

                    tipo = info.get(
                        "type",
                        "desconocido"
                    )

                    prompt += (
                        f"    - {parametro}"
                        f" ({tipo})"
                        f" | Requerido: {requerido}\n"
                    )

        prompt += """
    ```

    =========================
    INSTRUCCIONES
    =============

    * Responde de forma profesional.
    * Sé amable y natural.
    * No inventes información.
    * Utiliza las herramientas disponibles cuando necesites consultar o modificar información del sistema.
    * No inventes productos, precios, cotizaciones, estados ni información del cliente.
    * Si una herramienta no tiene la información necesaria, indícalo claramente.
    * Si una herramienta devuelve un error, intenta comprenderlo antes de responder.
    * Si necesitas información adicional del cliente para realizar una acción, solicítala.
    * Si necesitas ayuda de un asesor humano, indícalo.
    * Tu objetivo es ayudar al cliente y avanzar en el proceso comercial.

    =========================
    ESCALAMIENTO A HUMANO
    =====================

    Si consideras que la conversación debe ser atendida por un
    asesor humano (el cliente lo solicita explícitamente, hay una
    queja grave, una negociación fuera de tus reglas, o cualquier
    situación que no puedas resolver con las herramientas
    disponibles), inicia tu respuesta EXACTAMENTE con la etiqueta
    [ESCALAR_A_HUMANO] seguida de tu mensaje normal para el
    cliente. Ejemplo:

    [ESCALAR_A_HUMANO] Entiendo tu inquietud, en un momento un
    asesor de nuestro equipo se pondrá en contacto contigo.

    Usa esta etiqueta solo cuando sea necesario escalar. En
    cualquier otro caso, responde normalmente sin la etiqueta.
    """
    
        return prompt