"""Routes for scale-related endpoints."""

from collections.abc import Callable
from fastapi import APIRouter, Query
import semitone as st

from semitone_api.models import ScaleOut, ToneOut
from semitone_api.exceptions import InvalidNoteError, InvalidScaleTypeError

router = APIRouter(prefix="/scales", tags=["Scales"])

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
    octaves_above: int = Query(default=1, ge=0, le=4),
    octaves_below: int = Query(default=0, ge=0, le=4),
) -> ScaleOut:
    if scale_type not in SCALE_MAP:
        raise InvalidScaleTypeError(scale_type)
    try:
        scale = SCALE_MAP[scale_type](root)
        extended = scale.extend(
            octaves_below=octaves_below, octaves_above=octaves_above
        )
    except ValueError as exc:
        raise InvalidNoteError(root) from exc

    tones = [ToneOut(frequency_hz=t.freq) for t in extended.primaries]
    return ScaleOut(scale_type=scale_type, root=root, tones=tones)
