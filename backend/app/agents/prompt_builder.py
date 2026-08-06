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
=========================

{objetivo}

=========================
INFORMACIÓN DEL CLIENTE
=========================

Empresa: {prospecto.nombre_empresa}

Contacto: {prospecto.nombre_contacto or "No registrado"}

Ciudad: {prospecto.ciudad}

Estado comercial: {prospecto.estado.value}

=========================
REGLAS
=========================

"""

        for regla in reglas:
            prompt += f"- {regla}\n"

        prompt += """

=========================
HERRAMIENTAS DISPONIBLES
=========================

"""

        for tool in tools:

            prompt += (
                f"- {tool['name']}\n"
                f"  Descripción: {tool['description']}\n"
            )

            if tool["parameters"]:

                prompt += "  Parámetros:\n"

                for parametro, info in tool["parameters"].items():

                    requerido = (
                        "Sí"
                        if info.get("required", False)
                        else "No"
                    )

                    prompt += (
                        f"    - {parametro}"
                        f" ({info['type']})"
                        f" | Requerido: {requerido}\n"
                    )

            prompt += "\n"

        prompt += """

=========================
INSTRUCCIONES
=========================

- Responde de forma profesional.
- Sé amable y natural.
- No inventes información.
- Si necesitas consultar información del sistema, utiliza la herramienta adecuada.
- Si una herramienta no tiene la información necesaria, indícalo al cliente.
- Si necesitas ayuda de un asesor humano, indícalo.
- Tu objetivo es ayudar al cliente y avanzar en el proceso comercial.
"""

        return prompt