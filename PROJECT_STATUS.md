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
- Sourcing de prospectos desde Google Places API (New): endpoint
  `POST /api/v1/sourcing/buscar` (`tipo_negocio` + `zona` + `max_resultados`
  ≤20 + `dry_run`). Usa Text Search con field mask mínimo (`id`,
  `displayName`, `formattedAddress`, `internationalPhoneNumber`).
  Descarta negocios sin teléfono, deduplica por `google_place_id`
  (campo nuevo en `Prospecto`, migración `551353f12a2b`) y también
  recupera limpio si el teléfono ya existía en otro prospecto. Crea
  con `origen=GOOGLE_MAPS`, `estado=NUEVO`. Probado end-to-end con
  datos falsos de Google (dry_run, importación real, dedup, colisión
  de teléfono, `TipoNegocio.OTRO` rechazado) — **falta la prueba con
  la API real de Google** (`GOOGLE_PLACES_API_KEY` vacía en `.env`
  todavía) para validar formato de respuesta real y ver el costo en
  Cloud Console antes de escalar volumen.


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
- reglas de estado ajustadas tras encontrar falso positivo real

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
7. ~~Sourcing de prospectos vía Google Places API~~ ✅ construido,
   falta prueba con la API real de Google (ver abajo) antes de
   escalar volumen. El primer contacto saliente (WhatsApp con
   plantillas de marketing) es la fase siguiente, aún sin construir.

## Decisiones de diseño tomadas
- n8n es capa delgada de entrada/salida y notificaciones; toda la lógica
  de razonamiento del agente vive en código Python (nunca en n8n).
- Las transiciones de estado "mecánicas" (hechos objetivos, sin
  ambigüedad) van automatizadas en `DecisionEngine`. Las que requieren
  entender el contenido de la conversación las decide el modelo vía
  tool calling, guiado por reglas explícitas en `RuleEngine`.
- Modelo de OpenAI en uso: `gpt-5` vía Responses API (`client.responses.create`).

## Pendiente de verificar/decidir
- ✅ Confirmada con OpenAI real (no Mock) la máquina de estados
  completa en una sola conversación de varios turnos, con memoria
  real entre turnos: NUEVO→CONTACTADO→RESPONDIO (automáticas)
  →INTERESADO→COTIZADO→NEGOCIACION→CLIENTE (las 4 últimas guiadas por
  `RuleEngine` vía tool calling, incluyendo `gestionar_cotizacion`
  real). Prioridad 1 cerrada. En el camino se corrigieron 3 bugs:
  (1) el prompt nunca incluía el
  historial de mensajes → cada turno era una conversación nueva desde
  cero; (2) el prompt nunca incluía `prospecto.id` → el modelo no
  podía llamar `actualizar_estado`/`gestionar_cotizacion` (le faltaba
  un parámetro obligatorio) y terminaba pidiéndole al cliente su
  propio ID de base de datos; (3) `historial_estados.estado_anterior`/
  `estado_nuevo` seguían atados a un ENUM nativo de Postgres con un
  label viejo (`COTIZACION_ENVIADA` en vez de `COTIZADO`) nunca
  sincronizado tras un rename en el enum de Python — convertidas a
  `varchar` (migración `8f8f727f9685`), igual que ya se había hecho
  con `prospectos.estado`.
- Decidir si el payload del webhook `prospecto.cotizado` debe incluir el
  detalle completo de la cotización (hoy no lo trae).
- Falta correr la primera prueba real de sourcing contra Google Places
  API (New) — hoy `GOOGLE_PLACES_API_KEY` está vacía en `.env`. Cuando
  se configure, correr `POST /api/v1/sourcing/buscar` con
  `max_resultados` bajo (1-5) y `dry_run=true` primero, revisar los
  candidatos, y solo después repetir con `dry_run=false`. Revisar el
  costo en Google Cloud Console → Billing → Reports filtrado por SKU
  (el campo `internationalPhoneNumber` cae en un tier más caro que
  nombre/dirección solos).
- Decidir el formato canónico de teléfono (con o sin `+`/espacios/
  indicativo de país) cuando se construya la integración de WhatsApp:
  el `internationalPhoneNumber` que trae Google no necesariamente
  coincide con el formato que va a mandar n8n, y `ConversationService`
  hace match exacto por `telefono`.
