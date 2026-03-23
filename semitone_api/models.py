"""Models for the semitone API."""

from pydantic import BaseModel


class ToneOut(BaseModel):
    frequency_hz: float


class ScaleOut(BaseModel):
    scale_type: str  # e.g. "major"
    root: str  # e.g. "C"
    tones: list[ToneOut]
