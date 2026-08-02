class AIService:

    def responder(
        self,
        prompt: str,
        mensaje_usuario: str
    ):

        print("===== PROMPT =====")

        print("=" * 60)

        print(prompt)

        print("=" * 60)

        print("===== MENSAJE =====")

        print(mensaje_usuario)

        return (
            "Hola, gracias por escribirnos. "
            "En unos minutos uno de nuestros asesores "
            "te atenderá."
        )