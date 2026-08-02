from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str
    VERSION: str
    ENVIRONMENT: str

    API_PORT: int
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
    OPENAI_API_KEY: str | None = None

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