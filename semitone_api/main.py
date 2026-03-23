"""Main API program for the semitone API."""

from fastapi import FastAPI
import semitone as st

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/scale")
def scale(root: str, mode: str = "major"):
    frequencies = st.get_scale_frequencies(root=root, mode=mode)
    return {"root": root, "mode": mode, "frequencies": frequencies}
