# LeadFlow CRM — Estado del proyecto

## Qué es
CRM con agente de IA que gestiona prospectos y automatiza el proceso
comercial (no un chatbot simple: conoce el contexto del prospecto,
sigue reglas de negocio y usa herramientas conectadas al CRM).

**El código es genérico por diseño** (arquitectura de instancia
separada por cliente/silo, no multi-tenant — ver CLAUDE.md). El
negocio de cada instancia se configura por `.env`, nunca hardcodeado
en Python: `BUSINESS_NAME`, `BUSINESS_TYPE`, `BUSINESS_DESCRIPTION`,
`BUSINESS_TONE`. **Esta instancia en particular** hoy está configurada
para una empresa fabricante de cajas para pizza (ver `.env`) — eso es
un dato del `.env` de este deploy, no algo hardcodeado en el código.

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
  Descarta negocios sin teléfono, descarta números fijos colombianos
  (`descartado_telefono_fijo` — ver normalización de teléfono abajo,
  WhatsApp requiere celular), deduplica por `google_place_id` (campo
  nuevo en `Prospecto`, migración `551353f12a2b`) y también recupera
  limpio si el teléfono ya existía en otro prospecto. Crea con
  `origen=GOOGLE_MAPS`, `estado=NUEVO`. ✅ **Probado con la API real de
  Google** (billing activo, `GOOGLE_PLACES_API_KEY` configurada):
  búsqueda real "pizzerías en Palmira, Valle del Cauca" trajo 5
  resultados reales, de los cuales 2 eran números fijos (uno de ellos
  ni siquiera era una pizzería — "Comidas Rápidas Odie" — la búsqueda
  de texto libre de Google trae negocios relacionados aunque no sean
  pizzerías exactas; conocido, sin resolver — ver `includedType` como
  posible mejora futura si molesta). Nada se guardó (`dry_run`); el
  usuario confirmó el costo en su propio Google Cloud Billing.
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
  Business Manager para aprobación** (24-48h de review) — nombres
  genericados tras el refactor de `BUSINESS_*` (ver abajo), texto aún
  pendiente de re-redactar para reflejar el negocio vía esas variables:
  - `primer_contacto_negocio` (categoría Marketing, con opt-out) —
    para contacto en frío a negocios nuevos del sourcing de Google
    Places. Variable `{{1}} = nombre_empresa`.
  - `seguimiento_cotizacion` (categoría Marketing — no Utility,
    porque empuja a continuar la compra, con opt-out) — ya integrada
    en código (`SeguimientoService._renderizar_plantilla_seguimiento()`,
    usa `settings.BUSINESS_NAME`) pero el texto que hay que subir a
    Meta debe ser idéntico al que genera esa función. Variable
    `{{1}} = nombre_contacto` o `nombre_empresa` si no hay contacto.
  - Ninguna está conectada a un envío real todavía (no hay
    credenciales de Meta ni número verificado) — el nombre
    `seguimiento_cotizacion` en el código es solo la referencia
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
  test unitario (`backend/tests/test_telefono.py`, corridos
  con `pytest` — primera infraestructura de tests del proyecto,
  ver Comandos en CLAUDE.md) contra el formato real documentado por
  Google Places (`"+57 318 1329452"` → `"573181329452"`), el formato
  de alta manual sin indicativo, e idempotencia.
- ✅ Restricción de números fijos: `normalizar_telefono()` ahora
  rechaza números fijos colombianos (10 dígitos locales que no
  empiezan en `3`, ej. fijos de Cali/Valle `602...`, Bogotá `601...`)
  con `TelefonoFijoError` (subclase de `ValueError`, así que todo el
  manejo de errores existente — validadores de Pydantic,
  `SourcingService` — lo captura sin cambios). `SourcingService` lo
  reporta en su propia categoría `descartado_telefono_fijo`. Probado
  con datos reales de Google (ver sourcing arriba): detectó y
  descartó 2 fijos reales de la búsqueda en Palmira. Test unitario en
  `test_telefono.py` con el caso real de Google (`+57 602 2864126`) y
  un fijo de Bogotá.
- ✅ **Negocio genérico vía `.env`** (arquitectura de instancia
  separada por cliente/silo — ver CLAUDE.md): el contenido específico
  de "cajas de pizza" se sacó del código del módulo `agents/` y se
  movió a 4 variables nuevas en `Settings`/`.env`/`.env.example`
  (valores por defecto genéricos si no se configuran):
  `BUSINESS_NAME`, `BUSINESS_TYPE`, `BUSINESS_DESCRIPTION`,
  `BUSINESS_TONE`. `PromptBuilder` arma la identidad/tono del agente
  con estas 4 variables en vez de texto fijo. `RuleEngine` tenía dos
  ejemplos ilustrativos con "cajas"/"pizzería" (no reglas de negocio
  en sí) — genericados. `SeguimientoService` también tenía "cajas
  para pizza" hardcodeado en el texto de la plantilla de seguimiento
  (fuera de `agents/`, pero mismo problema) — ahora usa
  `settings.BUSINESS_NAME`; el nombre de esa plantilla también se
  genericó (`seguimiento_cotizacion_pizza` → `seguimiento_cotizacion`).
  **Fuera de alcance a propósito**: `SourcingService.TERMINOS_BUSQUEDA`/
  `TipoNegocio` (a qué tipo de negocios buscamos como *clientes*, ej.
  pizzerías) — es la categoría de prospecto objetivo, no la identidad
  de nuestro negocio; para un cliente de otro rubro esto es un cambio
  de enum/código, no una variable de `.env`. Probado end-to-end con
  OpenAI real usando los valores de cajas de pizza ya configurados en
  `.env`: memoria de conversación, tool calling, transiciones
  automáticas y guiadas (`NUEVO→CONTACTADO→RESPONDIO→INTERESADO`)
  siguen funcionando idéntico a antes del refactor — el agente sigue
  hablando de cajas de pizza porque eso es lo que dice el `.env` de
  esta instancia, no porque esté hardcodeado.
- ✅ Integración con **LeadFlow Control** (repo nuevo y separado, en
  `../leadflow-control` — plataforma de administración de cuentas,
  no forma parte de este repo). Este CRM ahora respeta el estado
  activo/inactivo de la cuenta:
  - `EstadoCuenta` (tabla nueva, fila única id=1) es el "interruptor"
    local. `POST /interno/estado-cuenta` (protegido por
    `EMPRESA_API_KEY`, comparación en tiempo constante vía
    `secrets.compare_digest`) lo actualiza cuando Control avisa un
    cambio.
  - `verificar_cuenta_activa` (dependency de FastAPI) aplicada a nivel
    de router en `conversacion.py`, `sourcing.py`, `seguimiento.py` —
    devuelve 403 de entrada si `activo=False`, antes de gastar un
    solo token de OpenAI.
  - Chequeo de respaldo cada 3 min (`APScheduler`, arrancado en el
    `lifespan` de `main.py`) contra `GET {CONTROL_BASE_URL}/empresas/mi-config`
    — mismo endpoint que también sirve `zona_busqueda_google_places`
    para sourcing (consulta perezosa, sin urgencia). A propósito NO
    usa n8n como reloj para esto (ver razón en `PROJECT_STATUS.md` de
    Control) — es el único mecanismo periódico de este proyecto que
    corre embebido en vez de disparado por n8n.
  - Instalación nueva sin `EstadoCuenta` todavía (nunca contactó a
    Control) → `activo=True` por defecto, no bloquea.
  - **Probado con integración real cruzando los dos repos** (Control
    corriendo en :8100, este CRM en :8000, comunicándose vía
    `host.docker.internal`): desactivar desde el panel de Control
    bloqueó este CRM automáticamente (403, sin llamar nada manual);
    reactivar directo en la base de Control (simulando que el push
    nunca llegó) dejó a este CRM desactivado hasta que el chequeo de
    respaldo lo corrigió — probado primero invocando la función
    manualmente, y **después, aparte, dejando correr el scheduler
    real sin tocar nada: se disparó solo a los 90 segundos** y
    bloqueó/corrigió la cuenta sin intervención — ver detalle completo
    en `PROJECT_STATUS.md` de `leadflow-control`.
  - Nuevas variables de entorno: `EMPRESA_API_KEY`, `CONTROL_BASE_URL`.
- ✅ **Tracking de uso de tokens de OpenAI**, reportado a Control
  (reemplaza el intento anterior de que Control consultara la API de
  gasto de OpenAI directo — se abandonó por requerir una Admin API Key
  de la organización del cliente). Tabla nueva `UsoTokens`
  (`prospecto_id` nullable, `origen` "conversacion"/"seguimiento",
  `modelo`, tokens entrada/salida/total). `OpenAIProvider.generate()`
  ahora devuelve `RespuestaIA` (texto + uso acumulado de TODAS las
  rondas de una llamada, incluyendo las de tool calling — antes solo
  devolvía el texto) en vez de un `str` plano; `MockProvider` devuelve
  uso en cero. `AgentPipeline._call_ai()` persiste el registro después
  de cada turno (tiene `db` disponible) y extrae el texto para seguir
  el flujo normal hacia `DecisionEngine` sin tocarlo. Un tercer job en
  el mismo `APScheduler` (una vez al día, sin la urgencia del chequeo
  de `activo`) suma el uso del día y lo reporta a
  `POST {CONTROL_BASE_URL}/empresas/reportar-uso`. Probado con
  conversación real (no simulada): 2 turnos reales con gpt-5
  capturaron 3918 y 3958 tokens respectivamente, el reporte a Control
  sumó correctamente 7876, y un segundo reporte el mismo día
  actualizó la misma fila en vez de duplicar (upsert por período del
  lado de Control).
- ✅ **Control de capacidad del embudo de prospección** (orquestador de
  "primer contacto" — no existía antes de esta sesión, aunque se había
  diseñado en una sesión previa: se detectó por grep que nunca se
  llegó a construir, y se construyó desde cero junto con las 3 reglas
  de negocio de una vez, en vez de como parche posterior):
  - `PrimerContactoService.ejecutar(dry_run)` (endpoint
    `POST /api/v1/primer-contacto/ejecutar`, mismo patrón que
    `seguimiento.py` — disparado por cron en n8n, sin scheduler
    embebido, porque es lógica de negocio no de disponibilidad) recorre
    prospectos `NUEVO` (más antiguos primero) y les manda
    `enviar_plantilla()` de `WhatsAppService` (nuevo — modo **simulado**
    hoy, sin `WHATSAPP_TOKEN`: loguea y devuelve éxito, igual que
    `MockProvider` con OpenAI; si hay token pero el envío real aún no
    está implementado, devuelve fallo controlado sin tumbar el resto
    del batch).
  - Corta en orden: fuera de horario laboral (`es_horario_laboral()`,
    nuevo, lun-vie 9-17 `America/Bogota`, con test unitario propio) →
    `pausar_prospeccion` activo → tope de embudo activo alcanzado →
    tope diario alcanzado (`MAXIMO_CONTACTOS_DIA = 10`, sin variable de
    entorno a propósito, no lo pidieron configurable). Cada corte
    devuelve `motivo_corte` explicando por qué, útil en `dry_run`.
  - **Tope de embudo activo** (`settings.TOPE_EMBUDO_ACTIVO`, default
    50, configurable por `.env`): cuenta prospectos en
    CONTACTADO/RESPONDIO/INTERESADO/COTIZADO/NEGOCIACION (reusa
    `ProspectoRepository.contar_por_estados()`, ya existía para las
    estadísticas) y si el total ya alcanzó el tope, no manda NINGÚN
    primer contacto nuevo ese día, sin importar cuántos `NUEVO` haya en
    cola.
  - Reintentos: si el envío falla, se registra `Evento`
    `PRIMER_CONTACTO_FALLIDO` (nuevo, junto con `PRIMER_CONTACTO_ENVIADO`
    — cupieron en el varchar(28) existente, sin migración) y el
    prospecto se reintenta en la próxima corrida, hasta
    `MAX_INTENTOS_PRIMER_CONTACTO = 3`, luego se deja de intentar
    (queda `NUEVO` para siempre, sin más reintentos automáticos).
  - **Pausa manual de prospección** (`pausar_prospeccion`): switch
    nuevo y **distinto** de `activo` — `activo` solo lo cambia el admin
    de Control (ej. por falta de pago) y bloquea TODO (403 en
    conversación/sourcing/seguimiento); `pausar_prospeccion` es más
    suave y **el propio cliente lo puede prender/apagar desde su panel**
    (confirmado con el usuario antes de construir): las conversaciones
    en curso siguen funcionando 100% normal, solo se detienen los
    primeros contactos nuevos. Vive en `Empresa.pausar_prospeccion`
    (Control) y se cachea localmente en `EstadoCuenta.pausar_prospeccion`
    (este repo) vía el mismo `GET /empresas/mi-config` y el mismo
    chequeo periódico de 3 min que ya existía para `activo` — sin
    mecanismo de comunicación nuevo. Expuesto en el panel cliente de
    Control por un endpoint angosto y dedicado
    (`POST /panel/cliente/prospeccion/pausar` / `/reanudar`), no por el
    `EmpresaUpdate` genérico de admin — es la primera acción de
    escritura que tiene el panel cliente (antes 100% solo lectura). El
    admin también puede pausar/reanudar desde su panel (mismo patrón
    visual que activar/desactivar). Ninguno de los dos toggles empuja
    al CRM al toque (a diferencia de `activo`) — se apoya en el poll de
    3 min, que ya corría por otra razón.
  - **Sourcing semanal**: `SourcingService.buscar()` ahora resuelve
    `tipo_negocio`/`zona` con fallback cuando no vienen en el request
    (`SourcingBuscarRequest` los volvió opcionales) —
    `settings.SOURCING_TIPO_NEGOCIO_DEFAULT` y
    `EstadoCuentaService.obtener_zona_busqueda()` (mismo caché de
    `zona_busqueda_google_places` que ya llegaba por el poll de 3 min,
    reusado tal cual) — pensado para que el disparo automático semanal
    desde un Cron Trigger de n8n no necesite conocer configuración de
    negocio. El cambio de diario a semanal es solo cuestión del cron de
    n8n (por ahorro de presupuesto), no de código.
  - ✅ **Probado end-to-end con datos reales** (no solo que importe):
    - Tope de embudo: bajando `TOPE_EMBUDO_ACTIVO` por debajo del
      conteo real de "en proceso" (6 en la base de prueba), la ejecución
      cortó con `"Tope de embudo activo alcanzado (6/5)"` y 0 evaluados.
    - Tope diario: con 10 eventos `PRIMER_CONTACTO_ENVIADO` reales
      insertados para hoy, cortó con `"Tope diario ya alcanzado
      (10/10)"`.
    - `dry_run=true` listó candidatos reales sin mutar nada (estado
      verificado sin cambios); `dry_run=false` sí mandó (simulado),
      cambió el estado a `CONTACTADO` vía `ProspectoService.cambiar_estado()`
      (historial + evento + webhook, no asignación directa) y registró
      el evento — confirmado en base de datos. **Nota**: esta corrida
      real de `dry_run=false` procesó también los `NUEVO` reales que ya
      existían en esta base de datos de desarrollo ("Pizzeria Fake
      Uno", "Test Normalizacion", "Test Fix Validador" — datos de
      prueba de sesiones anteriores, no un cliente real), que ahora
      están en `CONTACTADO`. Es el comportamiento correcto del
      orquestador, no un bug, pero queda anotado por si se esperaba
      verlos en `NUEVO`.
    - `pausar_prospeccion`: activado desde Control, confirmado que
      `GET /empresas/mi-config` lo refleja, confirmado que el poll de
      este CRM lo sincroniza a `EstadoCuenta` local, y confirmado que
      el orquestador corta específicamente con `"Prospección pausada
      por el cliente."` (no con el corte de horario laboral, que se
      evaluó aparte para aislar la causa) — mientras tanto,
      `GET /prospectos` y `/docs` siguieron respondiendo 200 normal,
      confirmando que solo bloquea el orquestador, nada más. Revertido
      a `false` al terminar la prueba.
    - Sourcing sin parámetros: `POST /sourcing/buscar` con
      `{"max_resultados": 1, "dry_run": true}` (sin `tipo_negocio` ni
      `zona`) armó la query `"pizzerías en Palmira, Valle del Cauca"`
      solo con los defaults, y trajo 1 resultado real de Google Places
      (`dry_run`, nada se guardó).
  - Nuevas variables de entorno: `TOPE_EMBUDO_ACTIVO`,
    `SOURCING_TIPO_NEGOCIO_DEFAULT`.
- ✅ **Estadísticas comerciales reportadas a Control** (cuarto job en
  el mismo `APScheduler`, una vez al día): cuántos prospectos
  respondieron alguna vez (`ProspectoRepository.contar_por_estados()`,
  estado `RESPONDIO` o más avanzado) y cuántos llegaron a `CLIENTE`.
  Snapshot del momento, no acumulado. Definiciones exactas acordadas
  con el usuario antes de construir (ver `PROJECT_STATUS.md` de
  `leadflow-control` para el detalle, incluyendo el margen de error
  conocido: `DESCARTADO` directo desde `NUEVO`/`CONTACTADO` sin haber
  respondido nunca se cuenta igual como "contactado", por simplicidad).
  Probado con la distribución real de prospectos de esta base — los
  números coincidieron exacto con el cálculo manual.


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
- `ProspectoResponse` heredaba el `field_validator` de teléfono desde
  `ProspectoBase` — reventaba `GET /prospectos` con 500 apenas la
  tabla tenía una fila con teléfono no normalizable (los 3 registros
  de prueba basura), porque el validador de escritura se re-ejecutaba
  también al leer/serializar. Movido el validador a `ProspectoCreate`
  únicamente — nunca validar de nuevo en el camino de lectura.

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
7. ~~Sourcing de prospectos vía Google Places API~~ ✅ construido y
   probado con la API real (ver arriba). El primer contacto saliente
   (WhatsApp con plantillas de marketing) es la fase siguiente — las
   plantillas ya están redactadas (ver arriba) pero sin subir a Meta
   ni conectado el envío real.
8. ~~Integración con LeadFlow Control (estado activo/inactivo)~~ ✅
   construida y probada con integración real entre los dos repos (ver
   arriba). El panel visual de Control ya existe (admin + cliente), ver
   `PROJECT_STATUS.md` de `leadflow-control`.
9. ~~Control de capacidad del embudo de prospección (orquestador de
   primer contacto, tope de embudo, pausa manual)~~ ✅ construido y
   probado end-to-end (ver arriba). Falta: registrar el Cron Trigger
   real en n8n (hoy se dispara manual, igual que seguimiento) y el
   envío real de WhatsApp (mismo pendiente que el resto de plantillas,
   ver arriba) — el orquestador ya está listo para conectarse apenas
   haya credenciales de Meta.

## Decisiones de diseño tomadas
- n8n es capa delgada de entrada/salida y notificaciones; toda la lógica
  de razonamiento del agente vive en código Python (nunca en n8n).
- Las transiciones de estado "mecánicas" (hechos objetivos, sin
  ambigüedad) van automatizadas en `DecisionEngine`. Las que requieren
  entender el contenido de la conversación las decide el modelo vía
  tool calling, guiado por reglas explícitas en `RuleEngine`.
- Modelo de OpenAI en uso: `gpt-5` vía Responses API (`client.responses.create`).
- Arquitectura de **instancia separada por cliente (silo)**, no
  multi-tenant compartido — al menos por ahora. Cada cliente corre su
  propio deploy completo (DB, API, n8n) con su propio `.env`. El
  negocio de la instancia se configura vía `BUSINESS_NAME`,
  `BUSINESS_TYPE`, `BUSINESS_DESCRIPTION`, `BUSINESS_TONE` — nunca
  hardcodeado en Python (ver detalle arriba y en CLAUDE.md).

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
- ✅ Prueba real de sourcing contra Google Places API (New) hecha
  (ver arriba). Pendiente: correr `dry_run=false` para importar de
  verdad los candidatos que el usuario confirme que se ven bien, y
  que el usuario confirme el costo exacto en su Billing (dijo que lo
  iba a mirar él mismo).
- ✅ Formato canónico de teléfono resuelto: E.164 sin `+` con
  indicativo `57` (ver `app/utils/telefono.py` arriba). Riesgo
  residual conocido y aceptado por ahora: la normalización asume
  números colombianos de 10 dígitos locales — si el negocio se
  expande a otro país, `normalizar_telefono()` hay que revisarla (hoy
  rechazaría números extranjeros válidos, tratándolos como
  inválidos).
