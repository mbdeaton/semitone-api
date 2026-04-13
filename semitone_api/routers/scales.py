"""Routes for scale-related endpoints."""

from collections.abc import Callable
from typing import Literal
from fastapi import APIRouter, Query
import semitone as st

from semitone_api.models import ScaleOut, ToneOut
from semitone_api.exceptions import InvalidNoteError

ScaleType = Literal["major", "minor", "chromatic"]
RootNote = Literal[
    "aflat", "a", "asharp",
    "bflat", "b",
    "c", "csharp",
    "dflat", "d", "dsharp",
    "eflat", "e",
    "f", "fsharp",
    "gflat", "g", "gsharp",
]

router = APIRouter(prefix="/scales", tags=["Scales"])


def normalize_root(root: str) -> str:
    """Convert URI-safe root note spelling to sharps/flats, e.g. 'csharp' -> 'C#'."""
    if root.endswith("sharp"):
        return f"{root[0].upper()}#"
    if root.endswith("flat"):
        return f"{root[0].upper()}b"
    return root.upper()


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
    scale_type: ScaleType,
    root: RootNote,
    octaves_above: int = Query(default=0, ge=0, le=4),
    octaves_below: int = Query(default=0, ge=0, le=4),
) -> ScaleOut:
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
