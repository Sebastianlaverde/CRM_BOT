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
- Tests unitarios: `docker compose exec api pytest` (o `pytest -v` /
  `pytest tests/archivo.py` para uno específico). Si agregás una
  dependencia nueva a `requirements.txt` (como `pytest`), un
  `restart` no la instala — hace falta
  `docker compose up -d --build api`.

## Arquitectura
- Capas: `models/` → `repositories/` → `services/` → `schemas/` → `routers/`
- Módulo aparte para IA: `agents/` (pipeline, tools, prompt builder,
  decision engine, context builder, rule engine, objective engine)
- Flujo del agente: `WhatsApp → n8n → API → ConversationService →
  CommercialAgent → AgentPipeline → OpenAI → Tools → PostgreSQL`
- **Instancia separada por cliente (silo), no multi-tenant**: este
  código está pensado para correr una instancia completa (DB, API,
  n8n) por cada cliente/negocio, no varios negocios compartiendo la
  misma base de datos. El negocio de la instancia actual **NO está
  hardcodeado** — vive en 4 variables de entorno (`BUSINESS_NAME`,
  `BUSINESS_TYPE`, `BUSINESS_DESCRIPTION`, `BUSINESS_TONE`, ver
  `.env.example`) que `PromptBuilder` inyecta en el prompt del agente.
  Para adaptar el proyecto a un cliente nuevo de otro rubro: llenar
  esas 4 variables en su propio `.env` — no hace falta tocar Python.
  Ojo: `SeguimientoService._renderizar_plantilla_seguimiento()`
  también usa `BUSINESS_NAME`, pero es el texto de una plantilla de
  WhatsApp — si cambia, hay que volver a aprobarla en Meta para ese
  cliente. `SourcingService.TERMINOS_BUSQUEDA`/`TipoNegocio` (a qué
  tipo de negocios buscamos como *clientes*, ej. pizzerías) es un
  eje aparte, no está en las 4 variables — sigue hardcodeado y hay
  que ajustarlo en código si el rubro del cliente busca otro tipo de
  prospecto.
- **LeadFlow Control** (repo separado, en `../leadflow-control`) es la
  plataforma donde se administran las cuentas de todos los clientes
  (activo/inactivo, config, login humano) — este repo NUNCA guarda
  contraseñas ni administra otras empresas, solo consulta/recibe su
  propio estado vía `EMPRESA_API_KEY`. Ver `PROJECT_STATUS.md` para
  el detalle de `EstadoCuenta`, `POST /interno/estado-cuenta`, y el
  chequeo periódico de respaldo (`APScheduler`, cada 3 min — la única
  pieza de este proyecto con un scheduler embebido en vez de n8n como
  reloj, a propósito, porque es un mecanismo de disponibilidad, no de
  negocio). Este CRM también le **reporta** a Control su propio uso
  de tokens de OpenAI una vez al día (`UsoTokens` →
  `POST /empresas/reportar-uso`, segundo job en el mismo scheduler) —
  Control nunca consulta la API de OpenAI directo, ver por qué en su
  `CLAUDE.md`. El mismo `GET /empresas/mi-config` (llamado por ese
  chequeo de 3 min) también trae `zona_busqueda_google_places` y
  `pausar_prospeccion`, cacheados en las mismas columnas de
  `EstadoCuenta` — no son solo el interruptor activo/inactivo aunque
  el nombre de la tabla lo sugiera.
- **Orquestador de primer contacto** (`PrimerContactoService`,
  `POST /api/v1/primer-contacto/ejecutar`): manda el mensaje inicial a
  prospectos `NUEVO`, con 3 frenos en orden (horario laboral →
  `pausar_prospeccion` → tope de embudo activo → tope diario) antes de
  enviar nada. `pausar_prospeccion` es distinto de `activo`: lo puede
  prender/apagar el propio cliente desde su panel de Control (no solo
  el admin), y solo frena primeros contactos nuevos — conversaciones en
  curso siguen andando igual. Si agregás un freno nuevo, seguí el mismo
  patrón: cortar temprano y devolver `motivo_corte` explicando por qué,
  no lanzar excepción.
- **`RespuestaIA`** (`app/agents/providers/respuesta_ia.py`) es el
  tipo de retorno de `BaseProvider.generate()` desde que se agregó el
  tracking de tokens — texto + uso acumulado. Si agregás un provider
  nuevo (Ollama/Gemini), tiene que devolver esto, no un `str` plano.

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
