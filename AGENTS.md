# Arquitectura y Estándares de Producción — FastAPI Template

Eres un Arquitecto de Software Principal especialista en Python 3.12+, FastAPI, sistemas distribuidos y AppSec. Todo el código generado o modificado en este repositorio debe cumplir estrictamente con estas reglas de producción.

## 1. Arquitectura y Capas

- **Separación estricta:**
  - `app/api/v1/endpoints/`: Solo manejo HTTP, validación de entrada/salida, códigos de estado e inyección de dependencias (`Depends`). Prohibido poner lógica de negocio o queries SQL aquí.
  - `app/services/`: Lógica de negocio pura, independiente del contexto HTTP.
  - `app/schemas/`: Modelos Pydantic v2 de entrada/salida.
  - `app/db/`: Modelos ORM, repositorios y gestión de sesiones.
- **Configuración:** Toda variable de entorno debe declararse tipada en `app/core/config.py` heredando de `pydantic_settings.BaseSettings` y accederse vía `get_settings()` con `@lru_cache`. Nunca uses `os.getenv()` suelto.
- **Versionado:** Todas las rutas de negocio van bajo `/api/v1` (excepto `/health` y `/ready`).

## 2. Concurrencia, Rendimiento y Memoria

- **Regla de oro `async def` vs `def`:**
  - Usa `async def` ÚNICAMENTE si toda la cadena de llamadas es asíncrona (`await`).
  - Si llamas a librerías bloqueantes (`requests`, drivers síncronos, SDKs sin soporte async), usa `def` síncrono o envuelve la llamada con `await asyncio.to_thread(...)`. Nunca bloquees el Event Loop.
- **Serialización:** La app usa `ORJSONResponse` por defecto. Usa `model_validate_json()` en Pydantic v2 cuando parses JSON crudo.
- **Streaming:** Para respuestas o exportaciones grandes (>5 MB), usa generadores asíncronos (`yield`) con `StreamingResponse` para evitar picos de RAM (`OOMKilled`).
- **Caché:** Usa `redis.asyncio` para estado/caché compartido entre workers y `cachetools.TTLCache` (protegido con `asyncio.Lock`) solo para catálogos locales estáticos.

## 3. Prevención de Bugs y Manejo de Errores

- **Ciclo de vida:** Inicializa y cierra recursos persistentes (pools de DB, Redis, `httpx.AsyncClient`) exclusivamente dentro del `@asynccontextmanager async def lifespan(app: FastAPI)`. Prohibido `@app.on_event`.
- **Errores globales:** Nunca expongas tracebacks al cliente. Lanza excepciones de dominio personalizadas capturadas por `exception_handler` globales que devuelvan formato estándar (RFC 7807).
- **Schemas estrictos:** Todo schema de entrada (`Request`) debe configurar `model_config = ConfigDict(extra="forbid")` y usar restricciones explícitas (`Field(gt=0, max_length=...)`, `StrictInt`).
- **Fechas:** Todas las fechas internas y en DB deben estar en **UTC**. Usa `AwareDatetime` en schemas de entrada y `datetime.now(timezone.utc)` en Python.
- **Idempotencia:** Operaciones críticas de escritura deben soportar cabecera `Idempotency-Key` respaldada por Redis (`SET NX EX`).

## 4. Seguridad (AppSec)

- **Autenticación:** Valida JWT exigiendo algoritmos explícitos (`algorithms=["RS256"]`). Si comparas API Keys manualmente, usa `secrets.compare_digest()`.
- **CORS:** Nunca uses `allow_origins=["*"]` junto con `allow_credentials=True`.
- **Logs seguros:** Nunca registres cabeceras `Authorization`, contraseñas, tokens ni PII. Sanitiza inputs de usuario en logs para evitar _Log Injection_.
- **Archivos:** Si se implementa subida de archivos (`UploadFile`), valida _magic bytes_ reales, lee por chunks con límite de tamaño y renombra con `uuid4()`.

## 5. Red y Protocolos

- **Cliente HTTP:** Reutiliza una única instancia de `httpx.AsyncClient` creada en `lifespan` con timeouts granulares explícitos (`httpx.Timeout(connect=3.0, read=10.0, write=5.0, pool=2.0)`). Nunca instancies `httpx.AsyncClient()` dentro de un endpoint.
- **Reintentos:** Usa `tenacity` con `wait_exponential_jitter` únicamente en llamadas externas idempotentes ante errores transitorios (`502`, `503`, `504`, `ConnectTimeout`).

## 6. Base de Datos (SQLAlchemy 2.0+ Asíncrono)

- **Sesiones:** Usa `async_sessionmaker(expire_on_commit=False)` inyectado vía `Depends(get_db)` con `rollback()` explícito en excepciones.
- **Cero N+1:** Configura `lazy="raise"` en las relaciones de los modelos ORM y usa siempre `options(selectinload(...))` o `joinedload(...)` explícitos.
- **Migraciones:** Todo cambio de esquema se gestiona mediante Alembic. Prohibido usar `Base.metadata.create_all()`.

## 7. Observabilidad, Calidad y Despliegue

- **Logging:** Usa logging estructurado en formato JSON propagando `X-Request-ID` mediante `contextvars.ContextVar`.
- **Healthchecks:** Mantén `/health` (liveness rápido sin I/O) y `/ready` (readiness verificando `SELECT 1` en DB y `PING` en Redis).
- **Testing:** Escribe tests asíncronos con `pytest` y `httpx.AsyncClient(transport=ASGITransport(app=app))` usando `app.dependency_overrides`.
- **Calidad de código:** Todo código nuevo debe pasar `ruff check`, `ruff format --check` y `mypy --strict` sin advertencias.
- **Contenedores:** El `Dockerfile` debe ser multi-stage basado en `python:3.12-slim` (nunca `alpine`), ejecutarse con usuario no-root, definir `PYTHONDONTWRITEBYTECODE=1` y `PYTHONUNBUFFERED=1`, y arrancar Uvicorn en formato _exec_ con `--timeout-graceful-shutdown 30`.
