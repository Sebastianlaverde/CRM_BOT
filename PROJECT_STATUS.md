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
- Seguimiento comercial automático: endpoint `POST /api/v1/seguimiento/ejecutar`
  (`dry_run`, disparado por cron en n8n — no hay scheduler embebido en
  la API). Detecta prospectos "esperando cliente" hace más de X días
  (umbral por estado en `SeguimientoService.UMBRAL_DIAS_POR_ESTADO`:
  CONTACTADO 3, RESPONDIO 2, INTERESADO 2, COTIZADO 3, NEGOCIACION 2;
  excluye CLIENTE/DESCARTADO/inactivos), genera el mensaje reusando
  `AgentPipeline` (modo seguimiento, sin mensaje entrante), lo registra
  como `Mensaje` IA + `Evento` `SEGUIMIENTO_ENVIADO`, y dispara webhook
  `prospecto.seguimiento`. Activó `SesionConversacion.estado`/
  `ultima_actividad` (existían en el modelo pero nunca se escribían).
  **No envía nada por WhatsApp de verdad todavía** — no existe esa
  integración; solo genera y registra. Probado end-to-end con datos
  reales (dry_run sin escribir nada, envío real con mensaje/evento/
  reset de `ultima_actividad` verificados en DB, no re-dispara
  inmediatamente, prospecto en `CLIENTE` queda excluido aunque su
  sesión esté vieja).
- ✅ Ventana de servicio de 24h de WhatsApp Business API respetada en
  el seguimiento: `SeguimientoService._horas_desde_ultimo_mensaje_cliente()`
  mide desde el último `Mensaje` con `autor=CLIENTE` (no desde
  `sesion.ultima_actividad`, que refleja cuándo respondió el AGENTE,
  no el cliente — hoy casi coinciden por el procesamiento síncrono,
  pero conceptualmente son cosas distintas). `<24h` → sigue generando
  texto libre vía `AgentPipeline` como antes. `>=24h` → NO llama a
  OpenAI, usa `_renderizar_plantilla_seguimiento()` con la plantilla
  `seguimiento_cotizacion_pizza` (pendiente de aprobación en Meta,
  ver más abajo), con fallback `nombre_contacto` → `nombre_empresa`.
  `SeguimientoResultado` ahora expone `canal_envio`
  (`"texto_libre"`/`"plantilla"`) y `plantilla` para que se vea en el
  `dry_run` cuál se usaría. **Hallazgo importante**: como
  `UMBRAL_DIAS_POR_ESTADO` son todos ≥ 2 días, en la práctica el
  seguimiento automático SIEMPRE cae en la rama de plantilla — el
  camino de texto libre casi no se usa con los umbrales actuales
  (quedaría para un futuro recordatorio same-day por debajo de 24h,
  no construido). Probado end-to-end: mensaje del cliente hace 13h →
  texto libre (con IA, contextual); mismo caso a 30h → plantilla, sin
  llamar a OpenAI (confirmado por tiempo de respuesta: 0.14s vs.
  decenas de segundos de las llamadas reales a gpt-5); fallback de
  nombre verificado con un prospecto sin `nombre_contacto` (de
  sourcing).
- Plantillas de WhatsApp redactadas y **pendientes de subir a Meta
  Business Manager para aprobación** (24-48h de review):
  - `primer_contacto_cajas_pizza` (categoría Marketing, con opt-out)
    — para contacto en frío a pizzerías nuevas del sourcing de Google
    Places. Variable `{{1}} = nombre_empresa`.
  - `seguimiento_cotizacion_pizza` (categoría Marketing — no Utility,
    porque empuja a continuar la compra, con opt-out) — ya integrada
    en código (`SeguimientoService._renderizar_plantilla_seguimiento()`)
    pero el texto que hay que subir a Meta debe ser idéntico al que
    genera esa función. Variable `{{1}} = nombre_contacto` o
    `nombre_empresa` si no hay contacto.
  - Ninguna está conectada a un envío real todavía (no hay
    credenciales de Meta ni número verificado) — el nombre
    `seguimiento_cotizacion_pizza` en el código es solo la referencia
    que se usará cuando se conecte el envío real; si Meta la rechaza
    o pide cambios de texto, hay que actualizar
    `_renderizar_plantilla_seguimiento()` para que coincida exacto
    con lo aprobado.
- Workflow de n8n para mensajes entrantes de WhatsApp:
  `n8n/workflows/whatsapp-inbound.json` (exportado, para importar
  manual vía "Import from File"). 6 nodos: `Webhook` → `Extraer datos
  de WhatsApp` (formato real de Meta Cloud API,
  `entry[0].changes[0].value.messages[0]`, asume `type=="text"` y un
  solo mensaje por payload) → `Transformar a formato API` (arma
  `{telefono, contenido, canal: "WHATSAPP"}` sin normalizar el
  teléfono — n8n se mantiene como capa delgada) → `HTTP Request` a
  `http://api:8000/api/v1/conversaciones/mensajes` (nombre del
  servicio docker, no localhost) con `onError: continueErrorOutput`
  → rama de éxito `Simular envío WhatsApp (placeholder)` (solo deja
  la respuesta lista, no envía nada real) / rama de error `Error - No
  se pudo procesar el mensaje`. Sin credenciales de Meta ni número
  verificado — el Webhook se dispara manual con un JSON de prueba
  (`payload.json` en la raíz del repo). ✅ Importado y probado por el
  usuario en su instancia de n8n — funcionó correctamente.
- Normalización de teléfono: `app/utils/telefono.py`
  (`normalizar_telefono()`) convierte cualquier entrada a formato
  E.164 sin `+` (solo dígitos, con indicativo `57`, ej.
  `573009999001`) — el mismo formato que exige la API de WhatsApp
  Business Cloud tanto para identificar quién escribe como para el
  futuro envío saliente. Aplicado como `field_validator` en
  `ProspectoCreate`/`ProspectoUpdate` (`schemas/prospecto.py`), así
  que se normaliza sin importar la puerta de entrada: alta manual,
  `SourcingService` (Google Places, con su propia categoría de
  descarte `descartado_telefono_invalido` para números que no
  calzan, sin tumbar el resto del batch), o el futuro envío de
  WhatsApp. Se hizo backfill de los 4 prospectos reales que ya
  existían sin indicativo (script one-off, no en el repo) — 3
  registros de prueba con teléfonos basura (`"string"`, `4332432`,
  `1521451`) se dejaron sin tocar, no son números reales.
  `payload.json` se actualizó al formato real de Meta (con
  indicativo) para que el test contra n8n siga siendo válido.
  Probado end-to-end: alta manual con y sin indicativo, teléfono
  inválido → 422 limpio, mensaje entrante con formato real de Meta
  (`573009999001`) encuentra correctamente al prospecto ya
  normalizado en la base (antes de este fix, este caso fallaba con
  "No existe un prospecto con ese teléfono"). Validado además con
  test unitario (`backend/tests/test_telefono.py`, 9 casos, corridos
  con `pytest` — primera infraestructura de tests del proyecto,
  ver Comandos en CLAUDE.md) contra el formato real documentado por
  Google Places (`"+57 318 1329452"` → `"573181329452"`), el formato
  de alta manual sin indicativo, e idempotencia.


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
4. ~~Seguimiento comercial (follow-ups automáticos)~~ ✅ construido
   (ver arriba). Falta conectar el cron real en n8n (hoy se dispara
   manual) y, más adelante, el envío real por WhatsApp.
5. Integración completa WhatsApp + n8n — en progreso: el workflow de
   n8n (entrada) está construido y **probado por el usuario en su
   instancia de n8n** ✅. El formato de teléfono también quedó resuelto
   (ver arriba). Falta: registrar el webhook de producción en Meta con
   un número verificado, y reemplazar el nodo placeholder por el envío
   real (credenciales de Meta + probablemente plantillas aprobadas
   para mensajes fuera de la ventana de 24h).
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
- ✅ Formato canónico de teléfono resuelto: E.164 sin `+` con
  indicativo `57` (ver `app/utils/telefono.py` arriba). Riesgo
  residual conocido y aceptado por ahora: la normalización asume
  números colombianos de 10 dígitos locales — si el negocio se
  expande a otro país, `normalizar_telefono()` hay que revisarla (hoy
  rechazaría números extranjeros válidos, tratándolos como
  inválidos).
