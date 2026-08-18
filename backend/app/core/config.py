from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "leadflow CRM"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str

    API_PORT: int = 8000
    TIMEZONE: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # n8n
    N8N_WEBHOOK_URL: str | None = None
    N8N_ENABLED: bool = True

    # OpenAI
    AI_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5"

    # Google Places (sourcing de prospectos)
    GOOGLE_PLACES_API_KEY: str = ""

    # Tipo de negocio objetivo por defecto para el sourcing automático
    # (disparado por n8n semanalmente, sin parámetros explícitos).
    SOURCING_TIPO_NEGOCIO_DEFAULT: str = "PIZZERIA"

    # Control de capacidad del embudo de prospección: tope de
    # prospectos "en proceso" (CONTACTADO/RESPONDIO/INTERESADO/
    # COTIZADO/NEGOCIACION) antes de que el orquestador de primer
    # contacto deje de enviar mensajes nuevos.
    TOPE_EMBUDO_ACTIVO: int = 50

    # Negocio (personalizar por cliente — arquitectura de instancia
    # separada por cliente, no multi-tenant. Un cliente nuevo solo
    # necesita llenar estas 4 variables, sin tocar Python).
    BUSINESS_NAME: str = "LeadFlow"
    BUSINESS_TYPE: str = "empresa comercial"
    BUSINESS_DESCRIPTION: str = "Vendemos productos y servicios a nuestros clientes."
    BUSINESS_TONE: str = "profesional y amable"

    # LeadFlow Control (plataforma de administración de cuentas —
    # proyecto separado). EMPRESA_API_KEY es la misma key que Control
    # generó al dar de alta esta empresa; se usa en ambas direcciones:
    # este CRM la manda al llamar a Control, y Control la manda al
    # llamar al endpoint /interno/estado-cuenta de este CRM.
    CONTROL_BASE_URL: str = ""
    EMPRESA_API_KEY: str = ""

    # WhatsApp
    WHATSAPP_TOKEN: str | None = None
    WHATSAPP_PHONE_ID: str | None = None
    WHATSAPP_VERIFY_TOKEN: str | None = None

    # Email
    SMTP_SERVER: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @cached_property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()