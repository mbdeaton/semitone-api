from fastapi import FastAPI
from semitone import get_scale_frequencies  # adjust to actual API

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/scale")
def scale(root: str, mode: str = "major"):
    frequencies = get_scale_frequencies(root=root, mode=mode)
    return {
        "root": root,
        "mode": mode,
        "frequencies": frequencies
    }
