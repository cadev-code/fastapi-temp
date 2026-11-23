# FastAPI Template

Plantilla base para desarrollar APIs con Python y FastAPI siguiendo una
estructura organizada por responsabilidades. El objetivo es que el equipo
pueda iniciar nuevos proyectos con una base común, clara y fácil de mantener.

## Inicialización del proyecto

Requisitos:

- Python entre 3.12 y 3.15, dentro del rango declarado en `pyproject.toml`.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado.

Después de clonar el repositorio, ejecuta:

```powershell
git clone <url-del-repositorio>
cd fastapi-template
uv sync
```

`uv sync` crea automáticamente el entorno virtual `.venv` e instala las
versiones exactas definidas en `uv.lock`. No es necesario ejecutar `uv venv`
por separado.

### Hooks de Git

Después de instalar las dependencias, activa los hooks de `pre-commit`:

```powershell
uv run pre-commit install
```

Esto registra las validaciones de Ruff y Gitleaks en el repositorio local.
Se ejecutarán automáticamente antes de cada commit. Para ejecutar todas las
validaciones manualmente sobre el proyecto:

```powershell
uv run pre-commit run --all-files
```

Los hooks locales pueden omitirse con `git commit --no-verify`, por lo que
CI/CD también debe ejecutar `uv run pre-commit run --all-files`.

### Integración continua y Pull Requests

El workflow de GitHub Actions definido en `.github/workflows/ci.yml` se ejecuta
cuando hay un `push` a `main`, `dev` o `qa`, y cuando se crea o actualiza un
Pull Request dirigido a cualquiera de esas ramas. Ejecuta las validaciones de
`pre-commit`, Mypy y Pytest.

Para impedir que un Pull Request se fusione cuando las validaciones fallen,
configura reglas de protección para `main`, `dev` y `qa` en GitHub:

1. Ve a **Settings → Branches** o **Rules → Rulesets**.
2. Activa **Require status checks to pass before merging**.
3. Selecciona el job `quality-and-test`.
4. Opcionalmente, exige Pull Requests, aprobaciones y ramas actualizadas.

Sin esta configuración, GitHub mostrará el fallo del CI, pero no
necesariamente bloqueará el merge.

Si existe un archivo `.env.example`, crea la configuración local:

```powershell
Copy-Item .env.example .env
```

Para activar manualmente el entorno virtual en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

También puedes ejecutar comandos sin activarlo:

```powershell
uv run uvicorn app.main:app --reload
```

### Configuración mediante variables de entorno

Las variables de entorno que controlan el comportamiento de la aplicación
deben declararse con su tipo en `app/core/config.py`, dentro de la clase
`Settings`. No uses `os.getenv()` directamente en otros módulos.

Al agregar una variable nueva:

1. Declárala en `Settings`, indicando si es obligatoria o incluyendo un valor
   predeterminado.
2. Agrégala también a `.env.example` para documentar la configuración
   necesaria para nuevos proyectos.
3. Usa `.env` para la configuración local. Este archivo no debe contenerse en
   el repositorio si incluye secretos.
4. Configura la variable directamente en el sistema de despliegue para
   `staging` y `production`.

Ejemplo:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
```

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/app
REDIS_URL=redis://localhost:6379
```

Pydantic carga los valores desde `.env` o desde las variables del sistema,
convierte sus tipos y reporta un error al iniciar si falta una variable
obligatoria.

#### Nivel de logging

La variable `LOG_LEVEL` define el nivel mínimo de mensajes que se registran.
Los niveles disponibles son `DEBUG`, `INFO`, `WARNING` y `ERROR`.

Valores recomendados:

```text
development → DEBUG
staging      → INFO
production   → INFO
```

`DEBUG` es útil durante el desarrollo, pero debe evitarse en producción porque
genera mucho ruido y puede registrar información innecesaria. En producción,
`INFO` permite observar eventos operativos importantes sin generar un volumen
excesivo de logs. Usa `WARNING` o `ERROR` únicamente si necesitas reducir aún
más el volumen.

### Instalación para producción

En producción, instala únicamente las dependencias de ejecución:

```powershell
uv sync --no-dev
```

Esto excluye herramientas como `pytest`, `ruff`, `mypy` y `pre-commit`,
reduciendo el tamaño del entorno y su superficie de ataque. Estas herramientas
deben ejecutarse durante CI/CD, no dentro de la imagen o entorno final de
producción.

Cuando se modifique `pyproject.toml`, actualiza el archivo de bloqueo y
sincroniza el entorno:

```powershell
uv lock
uv sync
```

## Objetivos

- Proporcionar una estructura inicial reutilizable para APIs con FastAPI.
- Separar la capa HTTP de la lógica de negocio.
- Facilitar la incorporación de servicios, repositorios, modelos y esquemas.
- Mantener convenciones comunes entre los proyectos del equipo.

## Estructura del proyecto

```text
app/
├── api/
│   ├── deps.py
│   └── v1/
│       ├── endpoints/
│       └── router.py
├── core/
│   ├── config.py
│   ├── exceptions.py
│   ├── logging.py
│   └── security.py
├── models/
├── repositories/
├── schemas/
├── services/
└── main.py
```

### Responsabilidad de cada capa

- `api`: endpoints, routers y dependencias relacionadas con HTTP.
- `core`: configuración, seguridad, logging y excepciones compartidas.
- `models`: modelos de persistencia o entidades del proyecto.
- `repositories`: acceso y operaciones sobre los datos.
- `schemas`: modelos de entrada y salida de la API.
- `services`: lógica de negocio y casos de uso.
- `main.py`: creación y configuración de la aplicación FastAPI.

### Archivos de ejemplo y código pendiente

Algunos archivos de esta plantilla pueden contener estructuras, clases o
métodos incompletos con fines ilustrativos. Por ejemplo,
`app\repositories\item_repository.py` muestra la estructura inicial de un
repositorio, pero sus métodos todavía no contienen consultas ni operaciones
reales de base de datos.

Al crear un proyecto a partir de esta plantilla:

- conserva y completa cada archivo de ejemplo que sea necesario;
- adapta el código a los modelos, reglas y necesidades del dominio;
- elimina los archivos de ejemplo que no se utilizarán, junto con cualquier
  referencia a ellos.

Estos archivos no se ignoran automáticamente. Si otra parte de la aplicación
los importa, deben implementarse o retirarse dichas referencias.

## Manejo de excepciones

`app\core\exceptions.py` contiene las excepciones propias del dominio:

- `DomainError`: clase base para errores de negocio.
- `NotFoundError`: indica que un recurso no existe.
- `BusinessRuleError`: indica que se violó una regla del negocio.

Los servicios deben lanzar estas excepciones sin depender directamente de
FastAPI o de códigos HTTP. Los handlers de FastAPI deben encargarse de
convertirlas en respuestas HTTP, por ejemplo `NotFoundError` en `404`.

Esto permite reutilizar la lógica de negocio desde endpoints, procesos en
segundo plano, comandos de consola y pruebas automatizadas.

## Convenciones de contribución

Antes de modificar o extender la plantilla, consulta
[`CONTRIBUTING.md`](CONTRIBUTING.md). Allí se documentan las reglas para crear
excepciones y las convenciones que deben seguir los proyectos basados en esta
plantilla.

## Uso como plantilla

Al crear un nuevo proyecto a partir de esta plantilla:

1. Conserva la separación entre las capas definidas.
2. Adapta modelos, esquemas, repositorios y servicios al dominio del proyecto.
3. Mantén las reglas documentadas en `CONTRIBUTING.md`.
4. Agrega nuevas convenciones al README o a `CONTRIBUTING.md` cuando sean
   aplicables a todos los proyectos del equipo.
