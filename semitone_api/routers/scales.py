"""Routes for scale-related endpoints."""

from collections.abc import Callable
from typing import Literal

from fastapi import APIRouter, Query
import semitone as st

from semitone_api.exceptions import InvalidNoteError
from semitone_api.models import ScaleOut, ToneOut


SCALE_FACTORIES: dict[str, Callable[[str], st.Scale]] = {
    "major": st.Major,
    "minor": st.Minor,
    "chromatic": st.Chromatic,
}
MODE_FACTORIES: dict[str, Callable[[str, int], st.Scale]] = {
    "diatonic-mode": st.DiatonicMode,
}
SERIES_FACTORIES: dict[str, Callable[[str, int], st.Scale]] = {
    "harmonic-octave": st.HarmonicOctave,
    "harmonic-series": st.HarmonicSeries,
}
ScaleType = Literal["major", "minor", "chromatic"]
RootNote = Literal[
    "aflat",
    "a",
    "asharp",
    "bflat",
    "b",
    "c",
    "csharp",
    "dflat",
    "d",
    "dsharp",
    "eflat",
    "e",
    "f",
    "fsharp",
    "gflat",
    "g",
    "gsharp",
]
router = APIRouter(prefix="/scales", tags=["Scales"])


def normalize_root(root: str) -> str:
    """Convert URI-safe note spellings, e.g. 'csharp' -> 'C#'."""
    if root.endswith("sharp"):
        return f"{root[0].upper()}#"
    if root.endswith("flat"):
        return f"{root[0].upper()}b"
    return root.upper()


def build_scale_out(
    scale: st.Scale,
    scale_type: str,
    normalized_root: str,
    octaves_below: int,
    octaves_above: int,
) -> ScaleOut:
    """Extend a scale and convert it to the API response model."""
    extended = scale.extend(
        octaves_below=octaves_below, octaves_above=octaves_above
    )
    tones = [ToneOut(frequency_hz=tone.freq) for tone in extended.primaries]
    return ScaleOut(scale_type=scale_type, root=normalized_root, tones=tones)


def validate_mode(mode: int) -> None:
    """Validate the requested diatonic mode index."""
    if mode < 1 or mode > 7:
        raise InvalidNoteError(f"mode must be 1-7, got {mode}")


def validate_max_multiplier(max_multiplier: int) -> None:
    """Validate the maximum harmonic multiplier."""
    if max_multiplier < 1:
        raise InvalidNoteError(
            f"max_multiplier must be >= 1, got {max_multiplier}"
        )


def handle_named_scale(
    scale_type: ScaleType,
    root: RootNote,
    octaves_below: int,
    octaves_above: int,
) -> ScaleOut:
    """Build a scale response for scales defined only by scale type and root."""
    normalized_root = normalize_root(root)
    try:
        scale = SCALE_FACTORIES[scale_type](normalized_root)
    except ValueError as exc:
        raise InvalidNoteError(root) from exc
    return build_scale_out(
        scale,
        scale_type,
        normalized_root,
        octaves_below,
        octaves_above,
    )


def handle_mode_scale(
    scale_type: Literal["diatonic-mode"],
    mode: int,
    root: RootNote,
    octaves_below: int,
    octaves_above: int,
) -> ScaleOut:
    """Build a scale response for scales defined by mode and root."""
    validate_mode(mode)
    normalized_root = normalize_root(root)
    try:
        scale = MODE_FACTORIES[scale_type](normalized_root, mode)
    except ValueError as exc:
        raise InvalidNoteError(root) from exc
    return build_scale_out(
        scale,
        scale_type,
        normalized_root,
        octaves_below,
        octaves_above,
    )


def handle_series_scale(
    scale_type: Literal["harmonic-octave", "harmonic-series"],
    max_multiplier: int,
    root: RootNote,
    octaves_below: int,
    octaves_above: int,
) -> ScaleOut:
    """Build a scale response for scales defined by max multiplier and root."""
    validate_max_multiplier(max_multiplier)
    normalized_root = normalize_root(root)
    try:
        scale = SERIES_FACTORIES[scale_type](normalized_root, max_multiplier)
    except ValueError as exc:
        raise InvalidNoteError(root) from exc
    return build_scale_out(
        scale,
        scale_type,
        normalized_root,
        octaves_below,
        octaves_above,
    )


@router.get(
    "/{scale_type}/{root}",
    response_model=ScaleOut,
    summary="Get a named scale",
    description=(
        "Returns the tones and frequencies for the requested named scale "
        "starting on the given root note."
    ),
)
def get_scale(
    scale_type: ScaleType,
    root: RootNote,
    octaves_below: int = Query(default=0, ge=0, le=4),
    octaves_above: int = Query(default=0, ge=0, le=4),
) -> ScaleOut:
    return handle_named_scale(
        scale_type,
        root,
        octaves_below,
        octaves_above,
    )


@router.get(
    "/diatonic-mode/{mode}/{root}",
    response_model=ScaleOut,
    summary="Get a diatonic mode scale",
    description=(
        "Returns the tones and frequencies for the requested diatonic mode "
        "scale starting on the given root note. "
        "Mode is an integer 1-7: 1=Ionian, 2=Dorian, 3=Phrygian, "
        "4=Lydian, 5=Mixolydian, 6=Aeolian, 7=Locrian."
    ),
)
def get_diatonic_mode(
    mode: int,
    root: RootNote,
    octaves_below: int = Query(default=0, ge=0, le=4),
    octaves_above: int = Query(default=0, ge=0, le=4),
) -> ScaleOut:
    return handle_mode_scale(
        "diatonic-mode",
        mode,
        root,
        octaves_below,
        octaves_above,
    )


@router.get(
    "/harmonic-octave/{max_multiplier}/{root}",
    response_model=ScaleOut,
    summary="Get a harmonic octave scale",
    description=(
        "Returns the tones and frequencies for the requested harmonic "
        "octave scale starting on the given root note. "
        "The harmonic series is reduced into the octave above the root. "
        "Duplicate tones are removed to produce unique primary tones."
    ),
)
def get_harmonic_octave(
    max_multiplier: int,
    root: RootNote,
    octaves_below: int = Query(default=0, ge=0, le=4),
    octaves_above: int = Query(default=0, ge=0, le=4),
) -> ScaleOut:
    return handle_series_scale(
        "harmonic-octave",
        max_multiplier,
        root,
        octaves_below,
        octaves_above,
    )


@router.get(
    "/harmonic-series/{max_multiplier}/{root}",
    response_model=ScaleOut,
    summary="Get a harmonic series scale",
    description=(
        "Returns the tones and frequencies for the requested harmonic "
        "series scale starting on the given root note. "
        "The harmonic series spans multiple octaves "
        "(2x, 3x, 4x, etc. the root frequency)."
    ),
)
def get_harmonic_series(
    max_multiplier: int,
    root: RootNote,
    octaves_below: int = Query(default=0, ge=0, le=4),
    octaves_above: int = Query(default=0, ge=0, le=4),
) -> ScaleOut:
    return handle_series_scale(
        "harmonic-series",
        max_multiplier,
        root,
        octaves_below,
        octaves_above,
    )
