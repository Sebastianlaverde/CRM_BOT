# LeadFlow CRM — Estado del proyecto

## Qué es
CRM para una empresa fabricante de cajas para pizza. Gestiona prospectos
y automatiza el proceso comercial con un agente de IA (no un chatbot
simple: conoce el contexto del prospecto, sigue reglas de negocio y usa
herramientas conectadas al CRM).

**Stack:** FastAPI + PostgreSQL + SQLAlchemy + Alembic + OpenAI (Responses
API con tool calling) + n8n + WhatsApp (aún no integrado).

**Arquitectura del agente:**
```
WhatsApp → n8n → API → ConversationService → CommercialAgent
→ AgentPipeline → OpenAI → Tools → PostgreSQL → respuesta
```

**Capas del backend:** models → repositories → services → schemas → routers,
más un módulo `agents/` aparte para todo lo de IA (pipeline, tools,
prompt builder, decision engine, etc.)

**Máquina de estados del prospecto** (en `ProspectoStateService.TRANSICIONES`):
```
NUEVO → CONTACTADO → RESPONDIO → INTERESADO → COTIZADO → NEGOCIACION → CLIENTE
                                      ↓ (desde cualquier estado intermedio)
                                 DESCARTADO
```

## Qué ya funciona (confirmado con pruebas reales)
- Tool calling real con OpenAI: el agente consulta productos reales en
  Postgres vía `buscar_productos` y responde con datos reales (validado
  con precio exacto, sin alucinación).
- Transiciones automáticas (mecánicas, sin criterio del modelo):
  `NUEVO→CONTACTADO` y `CONTACTADO→RESPONDIO`, disparadas por
  `DecisionEngine` y ejecutadas vía `ProspectoService.cambiar_estado()`
  (con validación, historial, evento, y webhook a n8n).
- Transiciones que requieren criterio (el modelo decide vía tool calling,
  guiado por reglas de `RuleEngine` que cambian según el estado actual):
  `RESPONDIO→INTERESADO`, `INTERESADO→COTIZADO` (al crear cotización),
  `COTIZADO→NEGOCIACION`, `NEGOCIACION→CLIENTE`, `→DESCARTADO`.
- Tool `gestionar_cotizacion`: el agente puede crear cotizaciones
  formales (productos + cantidades), consultarlas por ID o por prospecto.
  Usa `CotizacionService.crear_cotizacion()` (ya tenía validaciones
  robustas: prospecto activo, productos activos, precios válidos,
  transacciones con rollback).
- Escalamiento a humano: el modelo puede anteponer `[ESCALAR_A_HUMANO]`
  a su respuesta cuando lo considere necesario; queda registrado como
  `Evento` tipo `ESCALADO_A_HUMANO`.
- Webhooks a n8n en `prospecto.contactado` y `prospecto.cotizado`
  (payload trae solo datos del prospecto, no el detalle de la cotización
  — si n8n necesita el detalle, debe hacer `GET /cotizaciones` aparte).

## Bugs corregidos en esta sesión (por si algo similar reaparece)
Encontramos ~12 problemas, casi todos con un patrón común:
**inconsistencias de formato/nombre entre capas que nunca se habían
probado juntas de punta a punta** (parámetros de tools en dos formatos
distintos, métodos de repositorio con nombres que no coincidían con
quien los llamaba, un estado de enum que no existía, sintaxis rota que
bloqueaba imports, un campo de modelo usado sin existir, un estado
huérfano en la máquina de transiciones, y transiciones automáticas que
se saltaban toda la lógica de negocio). Ver historial de conversación
completo para detalle de cada uno.

## Qué falta (roadmap)
1. ~~Tool calling real con OpenAI~~ ✅
2. ~~Actualización automática de estados~~ ✅ (mecánicas + guiadas por reglas)
3. ~~Cotizaciones generadas por el agente~~ ✅
4. Seguimiento comercial (follow-ups automáticos, ej. recordar cotización
   sin respuesta después de X días) — pendiente
5. Integración completa WhatsApp + n8n (hoy solo existe el endpoint
   `POST /api/v1/conversaciones/mensajes`, pensado para que n8n lo llame
   tras recibir un webhook de WhatsApp — el lado de n8n no está construido)
6. Escalar a múltiples agentes (`AgentFactory` ya soporta el patrón,
   solo falta agregar más tipos además de `"commercial"`)

## Decisiones de diseño tomadas
- n8n es capa delgada de entrada/salida y notificaciones; toda la lógica
  de razonamiento del agente vive en código Python (nunca en n8n).
- Las transiciones de estado "mecánicas" (hechos objetivos, sin
  ambigüedad) van automatizadas en `DecisionEngine`. Las que requieren
  entender el contenido de la conversación las decide el modelo vía
  tool calling, guiado por reglas explícitas en `RuleEngine`.
- Modelo de OpenAI en uso: `gpt-5` vía Responses API (`client.responses.create`).

## Pendiente de verificar/decidir
- Confirmar en producción (con mensajes reales) que las reglas de
  `RuleEngine` llevan al modelo a actualizar estados correctamente en
  escenarios reales de conversación (probado hasta ahora con
  `MockProvider`, falta más prueba con OpenAI real en distintos
  escenarios).
- Decidir si el payload del webhook `prospecto.cotizado` debe incluir el
  detalle completo de la cotización (hoy no lo trae).
