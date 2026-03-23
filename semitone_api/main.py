"""Main API program for the semitone API."""

from importlib.metadata import metadata

from fastapi import FastAPI

from semitone_api.routers import scales
from semitone_api.exceptions import register_exception_handlers

_meta = metadata("semitone-api")

app = FastAPI(
    title=_meta["Name"],
    description=_meta["Summary"],
    version=_meta["Version"],
    contact={"name": _meta["Author"], "url": _meta["Project-URL"].split(", ")[1]},
    license_info={"name": _meta["License"]},
)

register_exception_handlers(app)
app.include_router(scales.router)


@app.get("/health", tags=["Meta"], summary="Health check")
def health():
    """Return a simple health check response."""
    return {"status": "ok"}
