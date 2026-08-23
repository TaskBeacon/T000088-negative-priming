from __future__ import annotations

import random
import statistics
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any

from psychopy import visual


@dataclass(frozen=True)
class PrimeProbePair:
    condition_id: str
    pair_index: int
    prime_target: str
    prime_distractor: str | None
    prime_reference: str
    prime_match: bool
    prime_correct_key: str
    probe_target: str
    probe_distractor: str
    probe_reference: str
    probe_match: bool
    probe_correct_key: str


def _balanced_labels(n_trials: int, labels: list[str], rng: random.Random) -> list[str]:
    if not labels:
        raise ValueError("Negative Priming conditions cannot be empty")
    counts = [n_trials // len(labels)] * len(labels)
    for index in range(n_trials % len(labels)):
        counts[index] += 1
    sequence = [label for label, count in zip(labels, counts) for _ in range(count)]
    for _ in range(100):
        rng.shuffle(sequence)
        if all(not (sequence[i] == sequence[i + 1] == sequence[i + 2] == sequence[i + 3]) for i in range(max(0, len(sequence) - 3))):
            return sequence
    return sequence


def _response_pairs(count: int, rng: random.Random) -> list[tuple[bool, bool]]:
    cycle = [(False, False), (True, True), (False, True), (True, False)]
    values = [cycle[index % len(cycle)] for index in range(count)]
    rng.shuffle(values)
    return values


def _choice_excluding(rng: random.Random, pool: list[str], excluded: set[str]) -> str:
    options = [item for item in pool if item not in excluded]
    if not options:
        raise ValueError("Shape pool is too small for the requested identity constraints")
    return rng.choice(options)


def generate_prime_probe_pairs(
    n_trials: int,
    condition_labels: list[Any] | None = None,
    *,
    seed: int = 0,
    shape_ids: list[str] | None = None,
    response_keys: dict[str, str] | None = None,
) -> list[PrimeProbePair]:
    """Preplan balanced prime-probe identities and match responses."""
    labels = [str(value) for value in (condition_labels or [])]
    allowed = {"no_distractor", "control", "negative_priming"}
    if set(labels) != allowed:
        raise ValueError(f"Expected exactly {sorted(allowed)}, got {sorted(set(labels))}")
    pool = [str(value) for value in (shape_ids or [])]
    if len(pool) < 8 or len(set(pool)) != len(pool):
        raise ValueError("Negative Priming requires at least eight unique shape IDs")
    keys = {str(k): str(v) for k, v in (response_keys or {}).items()}
    if set(keys) != {"different", "same"}:
        raise ValueError("response_keys must define different and same")

    rng = random.Random(int(seed))
    schedule = _balanced_labels(int(n_trials), labels, rng)
    counts = Counter(schedule)
    response_decks = {label: _response_pairs(counts[label], rng) for label in labels}
    response_indices = Counter()
    previous_probe: set[str] = set()
    plans: list[PrimeProbePair] = []

    for pair_index, condition_id in enumerate(schedule):
        prime_match, probe_match = response_decks[condition_id][response_indices[condition_id]]
        response_indices[condition_id] += 1

        prime_target = _choice_excluding(rng, pool, previous_probe)
        used_prime = {prime_target}
        prime_distractor = None
        if condition_id != "no_distractor":
            prime_distractor = _choice_excluding(rng, pool, previous_probe | used_prime)
            used_prime.add(prime_distractor)
        prime_reference = prime_target if prime_match else _choice_excluding(rng, pool, previous_probe | used_prime)
        used_prime.add(prime_reference)

        if condition_id == "negative_priming":
            probe_target = str(prime_distractor)
        else:
            probe_target = _choice_excluding(rng, pool, used_prime)
        probe_distractor = _choice_excluding(rng, pool, used_prime | {probe_target})
        probe_reference = (
            probe_target
            if probe_match
            else _choice_excluding(rng, pool, used_prime | {probe_target, probe_distractor})
        )
        previous_probe = {probe_target, probe_distractor, probe_reference}

        plans.append(
            PrimeProbePair(
                condition_id=condition_id,
                pair_index=pair_index,
                prime_target=prime_target,
                prime_distractor=prime_distractor,
                prime_reference=prime_reference,
                prime_match=prime_match,
                prime_correct_key=keys["same" if prime_match else "different"],
                probe_target=probe_target,
                probe_distractor=probe_distractor,
                probe_reference=probe_reference,
                probe_match=probe_match,
                probe_correct_key=keys["same" if probe_match else "different"],
            )
        )
    return plans


def decode_prime_probe_pair(condition: Any) -> dict[str, Any]:
    if not isinstance(condition, PrimeProbePair):
        raise ValueError(f"Expected a scheduled PrimeProbePair, got {condition!r}")
    return asdict(condition)


def _shape(win, vertices: list[list[float]], *, pos: list[float], scale: float, color: str):
    scaled = [(float(x) * scale, float(y) * scale) for x, y in vertices]
    return visual.ShapeStim(
        win=win,
        vertices=scaled,
        pos=tuple(float(value) for value in pos),
        lineColor=color,
        fillColor=None,
        lineWidth=4.0,
        closeShape=True,
    )


def build_shape_display(win, settings, plan: dict[str, Any], phase: str) -> list[Any]:
    """Construct the reference-aligned left compound and right reference shapes."""
    if phase not in {"prime", "probe"}:
        raise ValueError(f"Unsupported display phase: {phase}")
    specs = {str(k): value for k, value in dict(settings.shape_specs).items()}
    target_id = str(plan[f"{phase}_target"])
    distractor_value = plan.get(f"{phase}_distractor")
    distractor_id = str(distractor_value) if distractor_value is not None else None
    reference_id = str(plan[f"{phase}_reference"])
    left_pos = list(settings.layout["left_pos"])
    right_pos = list(settings.layout["right_pos"])
    scale = float(settings.layout["shape_scale"])
    colors = dict(settings.colors)

    stimuli: list[Any] = []
    if distractor_id is not None:
        stimuli.append(_shape(win, specs[distractor_id], pos=left_pos, scale=scale, color=str(colors["distractor"])))
    stimuli.append(_shape(win, specs[target_id], pos=left_pos, scale=scale, color=str(colors["target"])))
    stimuli.append(_shape(win, specs[reference_id], pos=right_pos, scale=scale, color=str(colors["reference"])))
    return stimuli


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    experimental = [row for row in rows if not bool(row.get("is_practice"))]
    accuracy = sum(bool(row.get("pair_correct")) for row in experimental) / len(experimental) if experimental else 0.0
    usable = [row for row in experimental if bool(row.get("pair_correct")) and row.get("probe_rt") is not None]
    by_condition: dict[str, list[float]] = {"negative_priming": [], "control": []}
    for row in usable:
        condition = str(row.get("condition_id"))
        if condition in by_condition:
            by_condition[condition].append(float(row["probe_rt"]))
    np_rt = statistics.median(by_condition["negative_priming"]) if by_condition["negative_priming"] else None
    control_rt = statistics.median(by_condition["control"]) if by_condition["control"] else None
    effect_ms = (np_rt - control_rt) * 1000.0 if np_rt is not None and control_rt is not None else None
    return {
        "accuracy": accuracy,
        "negative_priming_ms": effect_ms,
        "negative_priming_text": f"{effect_ms:.1f} ms" if effect_ms is not None else "数据不足",
    }
