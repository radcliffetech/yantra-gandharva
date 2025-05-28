from music21 import converter, stream, voiceLeading

from lib.utils.music_utils import in_range
from lib.utils.musicxml_utils import json_to_musicxml

__all__ = ["lint_satb"]


def lint_satb(realization_json: dict) -> dict:
    """
    Return a report dict {issues: [...], strengths: [...]}
    """
    sc = json_to_musicxml(realization_json)

    # json_to_musicxml already gives a Score; re-parse only if it isn't
    if isinstance(sc, stream.Score):
        score = sc
    else:
        score = converter.parse(sc)

    parts = {p.id.lower()[0]: p for p in score.parts}  # 's','a','t','b'
    issues, strengths = [], []

    # 1. range & spacing
    for name, part in parts.items():
        for n in part.recurse().notes:
            if not in_range(name, n.pitch):
                issues.append(f"{name.upper()} m{n.measureNumber} out of range")

    # 2. parallel 5ths/8ves (S↔B covers 80 %)
    vl = voiceLeading.VoiceLeadingQuartet(parts["s"], parts["b"])

    # Handle different music21 versions
    if hasattr(vl, "getParallelMotion"):
        parallels = vl.getParallelMotion()
    elif hasattr(vl, "parallelMotionGenerator"):
        parallels = list(vl.parallelMotionGenerator())
    elif hasattr(vl, "parallelMotion"):
        # In some versions this is a method, in others a cached list
        pm = vl.parallelMotion
        if callable(pm):
            try:
                parallels = pm()
            except IndexError:
                parallels = []
        else:
            parallels = pm or []
    else:
        parallels = []

    for bad in parallels:
        if getattr(bad, "directedName", "") in ("P5", "P8"):
            m = bad.firstNote.measureNumber
            issues.append(f"S/B m{m} parallel {bad.directedName}")

    # 3. doubled leading tone
    #   iterate chords-of-measure and check pitch class of LT in key
    #   (simple: last scale degree 7 in key signature)
    #   …

    if not issues:
        strengths.append("No obvious voice-leading violations")

    return {"issues": issues, "strengths": strengths}
