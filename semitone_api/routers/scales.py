"""Routes for scale-related endpoints."""

from collections.abc import Callable
import re
from fastapi import APIRouter, Query
import semitone as st

from semitone_api.models import ScaleOut, ToneOut
from semitone_api.exceptions import (
    InvalidNoteError,
    InvalidScaleTypeError,
)

router = APIRouter(prefix="/scales", tags=["Scales"])


def normalize_root(root: str) -> str:
    """Normalize URI-safe root note spelling, e.g. 'Csharp' -> 'C#'."""
    lowered = root.lower()
    if not re.fullmatch(r"[a-g](flat|sharp)?", lowered):
        raise InvalidNoteError(root)

    if lowered.endswith("sharp"):
        return f"{lowered[0].upper()}#"
    if lowered.endswith("flat"):
        return f"{lowered[0].upper()}b"
    return lowered.upper()


SCALE_MAP: dict[str, Callable[[str], st.Scale]] = {
    "major": st.Major,
    "minor": st.Minor,
    "chromatic": st.Chromatic,
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
    octaves_above: int = Query(default=0, ge=0, le=4),
    octaves_below: int = Query(default=0, ge=0, le=4),
) -> ScaleOut:
    if scale_type not in SCALE_MAP:
        raise InvalidScaleTypeError(scale_type)
    normalized_root = normalize_root(root)
    try:
        scale = SCALE_MAP[scale_type](normalized_root)
        extended = scale.extend(
            octaves_below=octaves_below, octaves_above=octaves_above
        )
    except ValueError as exc:
        raise InvalidNoteError(root) from exc

    tones = [ToneOut(frequency_hz=t.freq) for t in extended.primaries]
    display_root = normalized_root
    return ScaleOut(scale_type=scale_type, root=display_root, tones=tones)
