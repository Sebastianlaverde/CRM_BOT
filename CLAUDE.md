# LeadFlow CRM

CRM comercial con agente de IA (FastAPI + PostgreSQL + OpenAI tool
calling + n8n). Ver `PROJECT_STATUS.md` para el estado actual del
proyecto, qué está hecho y qué falta — ese archivo cambia seguido,
revísalo al inicio de cada sesión de trabajo.

## Comandos
- Levantar todo: `docker compose up -d --build`
- Logs: `docker compose logs -f api`
- Reiniciar solo la API: `docker compose restart api`
- Migraciones: `docker compose exec api alembic revision --autogenerate -m "mensaje"`
  luego `docker compose exec api alembic upgrade head`
  (siempre revisar el archivo generado antes de aplicar — autogenerate
  a veces detecta cambios no relacionados si el modelo Python y el
  historial de migraciones divergieron)

## Arquitectura
- Capas: `models/` → `repositories/` → `services/` → `schemas/` → `routers/`
- Módulo aparte para IA: `agents/` (pipeline, tools, prompt builder,
  decision engine, context builder, rule engine, objective engine)
- Flujo del agente: `WhatsApp → n8n → API → ConversationService →
  CommercialAgent → AgentPipeline → OpenAI → Tools → PostgreSQL`

## Reglas de arquitectura (aprendidas de bugs reales de este proyecto)
- **Tools del agente**: `BaseTool.parameters` siempre en formato plano
  `{"campo": {"type":..., "description":..., "enum":..., "required": bool}}`.
  `to_openai_function()` convierte esto al JSON Schema real que espera
  OpenAI — nunca dupliques esa conversión a mano en una tool nueva.
- **Cambios de estado de prospecto**: SIEMPRE a través de
  `ProspectoService.cambiar_estado()` (que delega en
  `ProspectoStateService`), nunca asignando `prospecto.estado = X`
  directo. Eso salta validación de transición, historial, evento y
  webhook a n8n.
- **Transiciones mecánicas vs con criterio**: si una transición de
  estado es un hecho objetivo (no requiere interpretar la conversación),
  va automatizada en `DecisionEngine.TRANSICIONES_AUTOMATICAS`. Si
  requiere criterio, es una regla en `RuleEngine` para que el modelo la
  dispare vía tool calling.
- **Nuevos campos de modelo**: si agregas un campo a un modelo
  SQLAlchemy, greppéalo también en repositories, tools, y schemas antes
  de dar por terminado — varios bugs de esta sesión fueron un campo
  usado en un lugar sin existir en el modelo.
- **Antes de dar por buena una tool o servicio nuevo**: probarlo
  end-to-end (no solo que importe) con datos reales, incluyendo el
  camino feliz Y al menos un caso de error esperado.

## Convenciones de estilo del código existente
El código del proyecto usa un estilo muy espaciado (un argumento por
línea, saltos de línea frecuentes). Sigue ese estilo al editar archivos
existentes para no mezclar convenciones dentro del mismo archivo.
