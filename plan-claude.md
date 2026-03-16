# Semitone API — MWE Build Plan

A step-by-step guide to building a minimal, production-shaped REST microservice
wrapping the `semitone` Python package, deployed on fly.io via Docker.

---

## Phase 1 — Project Scaffold

**Goal:** establish a clean directory structure before writing any logic.

1. Create the project directory (separate repo from `semitone` itself):
   ```
   semitone-api/
     app/
       __init__.py
       main.py
       models.py
       exceptions.py
       routers/
         __init__.py
         scales.py
         intervals.py
     tests/
       __init__.py
       test_scales.py
     Dockerfile
     fly.toml
     pyproject.toml
     README.md
     .dockerignore
     .gitignore
   ```

2. Initialize a git repo: `git init && git add . && git commit -m "scaffold"`

3. Create `pyproject.toml` with dependencies:
   ```toml
   [project]
   name = "semitone-api"
   version = "0.1.0"
   requires-python = ">=3.12"
   dependencies = [
     "fastapi>=0.111",
     "uvicorn[standard]>=0.29",
     "semitone",           # pulls from PyPI
   ]

   [project.optional-dependencies]
   dev = ["pytest", "httpx"]  # httpx is required by FastAPI's test client
   ```

---

## Phase 2 — Pydantic Models

**Goal:** define the shapes of all API inputs and outputs before writing routes.
Doing this first forces you to think about your API contract independently of implementation.

Edit `app/models.py`:

```python
from pydantic import BaseModel
from typing import List


class ToneOut(BaseModel):
    name: str           # e.g. "C4"
    frequency_hz: float


class ScaleOut(BaseModel):
    scale_type: str     # e.g. "major"
    root: str           # e.g. "C"
    tones: List[ToneOut]


class IntervalOut(BaseModel):
    tone_a: str
    tone_b: str
    semitones: int
    ratio: float        # frequency ratio tone_b / tone_a
```

Adjust fields to match what `semitone` actually exposes — these are starting shapes.

---

## Phase 3 — Exception Handling

**Goal:** ensure clients always get structured JSON errors, never raw Python tracebacks.

Edit `app/exceptions.py`:

```python
from fastapi import Request
from fastapi.responses import JSONResponse


class InvalidNoteError(Exception):
    def __init__(self, note: str):
        self.note = note


class InvalidScaleTypeError(Exception):
    def __init__(self, scale_type: str):
        self.scale_type = scale_type


def register_exception_handlers(app):
    @app.exception_handler(InvalidNoteError)
    async def invalid_note_handler(request: Request, exc: InvalidNoteError):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_note", "detail": f"'{exc.note}' is not a recognized note name."},
        )

    @app.exception_handler(InvalidScaleTypeError)
    async def invalid_scale_type_handler(request: Request, exc: InvalidScaleTypeError):
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_scale_type", "detail": f"'{exc.scale_type}' is not a supported scale type."},
        )
```

---

## Phase 4 — Routers

**Goal:** implement the two route modules. Keep each router focused on one resource.

### `app/routers/scales.py`

```python
from fastapi import APIRouter, Query
import semitone as st
from app.models import ScaleOut, ToneOut
from app.exceptions import InvalidNoteError, InvalidScaleTypeError

router = APIRouter(prefix="/scales", tags=["Scales"])

SCALE_MAP = {
    "major": st.Major,
    "harmonic": st.HarmonicOctave,
    # extend as semitone grows
}


@router.get(
    "/{scale_type}/{root}",
    response_model=ScaleOut,
    summary="Get a scale",
    description=(
        "Returns all tones and frequencies for a named scale "
        "starting on a given root note."
    ),
)
def get_scale(
    scale_type: str,
    root: str,
    octaves_above: int = Query(default=1, ge=0, le=4),
    octaves_below: int = Query(default=0, ge=0, le=4),
):
    if scale_type not in SCALE_MAP:
        raise InvalidScaleTypeError(scale_type)
    try:
        scale = SCALE_MAP[scale_type](root)
        extended = scale.extend(octaves_below=octaves_below, octaves_above=octaves_above)
    except Exception:
        raise InvalidNoteError(root)

    tones = [ToneOut(name=t.name, frequency_hz=t.frequency) for t in extended]
    return ScaleOut(scale_type=scale_type, root=root, tones=tones)
```

> Adapt the `semitone` API calls to match actual method names from the package.

### `app/routers/intervals.py`

```python
from fastapi import APIRouter
import semitone as st
from app.models import IntervalOut
from app.exceptions import InvalidNoteError

router = APIRouter(prefix="/intervals", tags=["Intervals"])


@router.get(
    "/{tone_a}/{tone_b}",
    response_model=IntervalOut,
    summary="Get interval between two tones",
    description="Returns the interval in semitones and the frequency ratio between two named tones.",
)
def get_interval(tone_a: str, tone_b: str):
    try:
        a = st.Tone(tone_a)
        b = st.Tone(tone_b)
    except Exception:
        bad = tone_a  # refine if semitone raises distinguishable errors
        raise InvalidNoteError(bad)

    semitones = b.semitone_index - a.semitone_index
    ratio = b.frequency / a.frequency
    return IntervalOut(tone_a=tone_a, tone_b=tone_b, semitones=semitones, ratio=ratio)
```

---

## Phase 5 — Main App

**Goal:** wire everything together in `app/main.py`.

```python
from fastapi import FastAPI
from app.routers import scales, intervals
from app.exceptions import register_exception_handlers

app = FastAPI(
    title="Semitone API",
    description=(
        "A REST microservice for analyzing musical scales and tone relationships. "
        "Backed by the [semitone](https://github.com/mbdeaton/semitone) Python package."
    ),
    version="0.1.0",
    contact={"name": "mbdeaton", "url": "https://github.com/mbdeaton/semitone"},
    license_info={"name": "GPL-3.0"},
)

register_exception_handlers(app)
app.include_router(scales.router)
app.include_router(intervals.router)


@app.get("/health", tags=["Meta"], summary="Health check")
def health():
    return {"status": "ok"}
```

The `/health` endpoint is required by fly.io's health checks and is good practice generally.

---

## Phase 6 — Tests

**Goal:** write at least one happy-path and one error-path test per router before touching Docker.
Catching bugs now is far cheaper than debugging in a container.

Edit `tests/test_scales.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_major_scale_c():
    r = client.get("/scales/major/C")
    assert r.status_code == 200
    body = r.json()
    assert body["scale_type"] == "major"
    assert body["root"] == "C"
    assert len(body["tones"]) > 0


def test_invalid_scale_type():
    r = client.get("/scales/dorian/C")
    assert r.status_code == 400
    assert r.json()["error"] == "invalid_scale_type"


def test_invalid_root_note():
    r = client.get("/scales/major/Z9")
    assert r.status_code == 400


def test_interval():
    r = client.get("/intervals/C4/G4")
    assert r.status_code == 200
    body = r.json()
    assert body["semitones"] == 7
```

Run with: `pytest tests/`

---

## Phase 7 — Dockerfile

**Goal:** a minimal, secure image.

```dockerfile
FROM python:3.12-slim

# Run as non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install dependencies first (layer caching)
COPY --chown=appuser pyproject.toml .
RUN pip install --no-cache-dir --user .

# Copy application code
COPY --chown=appuser app/ ./app/

ENV PATH="/home/appuser/.local/bin:$PATH"

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Create `.dockerignore`:
```
__pycache__
*.pyc
.git
tests/
*.md
fly.toml
```

Build and test locally:
```bash
docker build -t semitone-api .
docker run -p 8080:8080 semitone-api
# Visit http://localhost:8080/docs to confirm the Swagger UI loads
```

---

## Phase 8 — fly.io Deployment

**Goal:** deploy the container to fly.io.

1. Install the fly CLI: https://fly.io/docs/hands-on/install-flyctl/

2. Authenticate: `fly auth login`

3. Launch the app (run from project root — fly detects the Dockerfile):
   ```bash
   fly launch
   ```
   Accept the generated `fly.toml`. When asked about Postgres or Redis, say no.

4. Edit the generated `fly.toml` to confirm the port matches your Dockerfile:
   ```toml
   [[services]]
     internal_port = 8080
     protocol = "tcp"

     [[services.tcp_checks]]
       interval = "15s"
       timeout = "5s"
       grace_period = "5s"
   ```

5. Add a health check path (fly.io can poll `/health`):
   ```toml
   [[services.http_checks]]
     interval = "15s"
     timeout = "5s"
     grace_period = "10s"
     method = "GET"
     path = "/health"
   ```

6. Deploy:
   ```bash
   fly deploy
   ```

7. Verify:
   ```bash
   fly status
   fly logs
   ```
   Then visit `https://<your-app>.fly.dev/docs` to confirm the live Swagger UI.

---

## Phase 9 — README

**Goal:** write a `README.md` that a developer can read in 2 minutes and immediately try the API.

It should contain:

- One-sentence description of what the API does
- Base URL (your fly.dev URL)
- Link to `/docs` for interactive docs
- 3–5 example `curl` commands:
  ```bash
  # Get a C major scale
  curl https://<your-app>.fly.dev/scales/major/C

  # Get a scale spanning 2 octaves above
  curl "https://<your-app>.fly.dev/scales/major/C?octaves_above=2"

  # Get the interval between C4 and G4
  curl https://<your-app>.fly.dev/intervals/C4/G4

  # Health check
  curl https://<your-app>.fly.dev/health
  ```
- A note that the full OpenAPI spec is available at `/openapi.json`

---

## Checklist Summary

| Phase | Task | Done |
|-------|------|------|
| 1 | Project scaffold & pyproject.toml | ☐ |
| 2 | Pydantic models | ☐ |
| 3 | Exception handlers | ☐ |
| 4 | Scales & intervals routers | ☐ |
| 5 | Main app wiring | ☐ |
| 6 | Tests passing locally | ☐ |
| 7 | Docker build & local smoke test | ☐ |
| 8 | fly.io deployment live | ☐ |
| 9 | README with curl examples | ☐ |

---

## Notes & Pitfalls

- **Adapt semitone calls to the real API.** The method names in Phases 4 (`t.name`, `t.frequency`,
  `t.semitone_index`, `st.Tone`) are illustrative — verify against the actual `semitone` source
  before writing the routers.

- **Don't version URLs yet.** Add `/v1/` prefixes only when you need to break backward compatibility.

- **Keep routes read-only (`GET` only).** `semitone` is a pure analysis library; there is nothing
  to create or mutate. Resist the urge to add `POST` endpoints until there's a real reason.

- **The `/docs` UI is your live documentation.** Share that URL rather than writing separate
  API reference docs — it stays in sync automatically.

- **fly.io free tier** spins down idle machines. For a learning project this is fine; for
  production add `min_machines_running = 1` in `fly.toml`.