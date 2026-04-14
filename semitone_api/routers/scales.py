"""Routes for scale-related endpoints."""

from collections.abc import Callable
from typing import Literal
from fastapi import APIRouter, Query
import semitone as st

from semitone_api.models import ScaleOut, ToneOut
from semitone_api.exceptions import InvalidNoteError


# Factory functions for scales that don't take a root note as the only parameter
def create_diatonic_mode(root: str, mode: int) -> st.DiatonicMode:
    """Create a DiatonicMode scale."""
    return st.DiatonicMode(root, mode)


def create_harmonic_octave(root: str, max_multiplier: int) -> st.HarmonicOctave:
    """Create a HarmonicOctave scale."""
    return st.HarmonicOctave(root, max_multiplier)


def create_harmonic_series(root: str, max_multiplier: int) -> st.HarmonicSeries:
    """Create a HarmonicSeries scale."""
    return st.HarmonicSeries(root, max_multiplier)


SCALE_FACTORIES: dict[str, Callable[[str], st.Scale]] = {
    "major": st.Major,
    "minor": st.Minor,
    "chromatic": st.Chromatic,
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
    octaves_below: int = Query(default=0, ge=0, le=4),
    octaves_above: int = Query(default=0, ge=0, le=4),
) -> ScaleOut:
    normalized_root = normalize_root(root)
    try:
        scale = SCALE_FACTORIES[scale_type](normalized_root)
        extended = scale.extend(
            octaves_below=octaves_below, octaves_above=octaves_above
        )
    except ValueError as exc:
        raise InvalidNoteError(root) from exc

    tones = [ToneOut(frequency_hz=t.freq) for t in extended.primaries]
    display_root = normalized_root
    return ScaleOut(scale_type=scale_type, root=display_root, tones=tones)


@router.get(
    "/diatonic-mode/{mode}/{root}",
    response_model=ScaleOut,
    summary="Get a diatonic mode",
    description=(
        "Returns all tones and frequencies for a diatonic mode "
        "starting on a given root note. "
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
    if mode < 1 or mode > 7:
        raise InvalidNoteError(f"mode must be 1-7, got {mode}")

    normalized_root = normalize_root(root)
    try:
        scale = create_diatonic_mode(normalized_root, mode)
        extended = scale.extend(
            octaves_below=octaves_below, octaves_above=octaves_above
        )
    except ValueError as exc:
        raise InvalidNoteError(root) from exc

    tones = [ToneOut(frequency_hz=t.freq) for t in extended.primaries]
    display_root = normalized_root
    return ScaleOut(scale_type="diatonic-mode", root=display_root, tones=tones)


@router.get(
    "/harmonic-octave/{max_multiplier}/{root}",
    response_model=ScaleOut,
    summary="Get a harmonic octave scale",
    description=(
        "Returns all tones and frequencies for a harmonic octave scale "
        "starting on a given root note. "
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
    if max_multiplier < 1:
        raise InvalidNoteError(
            f"max_multiplier must be >= 1, got {max_multiplier}"
        )

    normalized_root = normalize_root(root)
    try:
        scale = create_harmonic_octave(normalized_root, max_multiplier)
        extended = scale.extend(
            octaves_below=octaves_below, octaves_above=octaves_above
        )
    except ValueError as exc:
        raise InvalidNoteError(root) from exc

    tones = [ToneOut(frequency_hz=t.freq) for t in extended.primaries]
    display_root = normalized_root
    return ScaleOut(
        scale_type="harmonic-octave", root=display_root, tones=tones
    )


@router.get(
    "/harmonic-series/{max_multiplier}/{root}",
    response_model=ScaleOut,
    summary="Get a harmonic series scale",
    description=(
        "Returns all tones and frequencies for a harmonic series scale "
        "starting on a given root note. "
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
    if max_multiplier < 1:
        raise InvalidNoteError(
            f"max_multiplier must be >= 1, got {max_multiplier}"
        )

    normalized_root = normalize_root(root)
    try:
        scale = create_harmonic_series(normalized_root, max_multiplier)
        extended = scale.extend(
            octaves_below=octaves_below, octaves_above=octaves_above
        )
    except ValueError as exc:
        raise InvalidNoteError(root) from exc

    tones = [ToneOut(frequency_hz=t.freq) for t in extended.primaries]
    display_root = normalized_root
    return ScaleOut(
        scale_type="harmonic-series", root=display_root, tones=tones
    )
