from __future__ import annotations

from functools import partial
from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context

from .utils import build_shape_display, decode_prime_probe_pair


def _context(unit: StimUnit, *, trial_id: int, block_id: str, condition_id: str, phase: str, deadline: float, valid_keys: list[str], stim_id: str, factors: dict[str, Any]) -> None:
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=deadline,
        valid_keys=valid_keys,
        block_id=block_id,
        condition_id=condition_id,
        task_factors=factors,
        stim_id=stim_id,
    )


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
    is_practice=False,
):
    plan = decode_prime_probe_pair(condition)
    condition_id = str(plan["condition_id"])
    trial_id = next_trial_id()
    current_block = str(block_id or "block")
    valid_keys = [str(settings.response_keys["different"]), str(settings.response_keys["same"])]
    prime_response_triggers = {
        str(settings.response_keys["different"]): settings.triggers.get("response_different"),
        str(settings.response_keys["same"]): settings.triggers.get("response_same"),
    }
    probe_response_triggers = {
        str(settings.response_keys["different"]): settings.triggers.get("probe_response_different"),
        str(settings.response_keys["same"]): settings.triggers.get("probe_response_same"),
    }
    factors = {
        "condition_id": condition_id,
        "pair_index": int(plan["pair_index"]),
        "prime_target": plan["prime_target"],
        "prime_distractor": plan.get("prime_distractor"),
        "prime_reference": plan["prime_reference"],
        "prime_match": bool(plan["prime_match"]),
        "prime_correct_key": str(plan["prime_correct_key"]),
        "probe_target": plan["probe_target"],
        "probe_distractor": plan["probe_distractor"],
        "probe_reference": plan["probe_reference"],
        "probe_match": bool(plan["probe_match"]),
        "probe_correct_key": str(plan["probe_correct_key"]),
    }
    data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": current_block,
        "block_idx": int(block_idx or 0),
        "condition": condition_id,
        "condition_id": condition_id,
        "pair_index": int(plan["pair_index"]),
        "is_practice": bool(is_practice),
        **factors,
    }
    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    trigger_runtime.send(settings.triggers.get("ready"))
    ready = make_unit(unit_label="ready").add_stim(stim_bank.get("ready_prompt"))
    _context(ready, trial_id=trial_id, block_id=current_block, condition_id=condition_id, phase="ready", deadline=0.0, valid_keys=["space"], stim_id="ready_prompt", factors=factors)
    ready.wait_and_continue(keys=["space"]).to_dict(data)

    pre_blank = make_unit(unit_label="pre_pair_blank").add_stim(stim_bank.get("blank_screen"))
    _context(pre_blank, trial_id=trial_id, block_id=current_block, condition_id=condition_id, phase="pre_pair_blank", deadline=float(settings.ready_blank_duration), valid_keys=[], stim_id="blank_screen", factors=factors)
    pre_blank.show(duration=float(settings.ready_blank_duration), onset_trigger=settings.triggers.get("pre_pair_blank")).to_dict(data)

    prime_fix = make_unit(unit_label="prime_fixation").add_stim(stim_bank.get("fixation"))
    _context(prime_fix, trial_id=trial_id, block_id=current_block, condition_id=condition_id, phase="prime_fixation", deadline=float(settings.fixation_duration), valid_keys=[], stim_id="fixation", factors=factors)
    prime_fix.show(duration=float(settings.fixation_duration), onset_trigger=settings.triggers.get("prime_fixation")).to_dict(data)

    prime = make_unit(unit_label="prime_response").add_stim(build_shape_display(win, settings, plan, "prime"))
    _context(prime, trial_id=trial_id, block_id=current_block, condition_id=condition_id, phase="prime_response", deadline=float(settings.response_timeout), valid_keys=valid_keys, stim_id=f"{condition_id}_prime", factors=factors)
    prime.capture_response(
        keys=valid_keys,
        duration=float(settings.response_timeout),
        onset_trigger=settings.triggers.get(f"prime_{condition_id}"),
        response_trigger=prime_response_triggers,
        timeout_trigger=settings.triggers.get("prime_timeout"),
        correct_keys=[str(plan["prime_correct_key"])],
    ).to_dict(data)

    inter_blank = make_unit(unit_label="inter_display_blank").add_stim(stim_bank.get("blank_screen"))
    _context(inter_blank, trial_id=trial_id, block_id=current_block, condition_id=condition_id, phase="inter_display_blank", deadline=float(settings.inter_display_duration), valid_keys=[], stim_id="blank_screen", factors=factors)
    inter_blank.show(duration=float(settings.inter_display_duration), onset_trigger=settings.triggers.get("inter_display_blank")).to_dict(data)

    probe_fix = make_unit(unit_label="probe_fixation").add_stim(stim_bank.get("fixation"))
    _context(probe_fix, trial_id=trial_id, block_id=current_block, condition_id=condition_id, phase="probe_fixation", deadline=float(settings.fixation_duration), valid_keys=[], stim_id="fixation", factors=factors)
    probe_fix.show(duration=float(settings.fixation_duration), onset_trigger=settings.triggers.get("probe_fixation")).to_dict(data)

    probe = make_unit(unit_label="probe_response").add_stim(build_shape_display(win, settings, plan, "probe"))
    _context(probe, trial_id=trial_id, block_id=current_block, condition_id=condition_id, phase="probe_response", deadline=float(settings.response_timeout), valid_keys=valid_keys, stim_id=f"{condition_id}_probe", factors=factors)
    probe.capture_response(
        keys=valid_keys,
        duration=float(settings.response_timeout),
        onset_trigger=settings.triggers.get(f"probe_{condition_id}"),
        response_trigger=probe_response_triggers,
        timeout_trigger=settings.triggers.get("probe_timeout"),
        correct_keys=[str(plan["probe_correct_key"])],
    ).to_dict(data)

    prime_correct = bool(prime.get_state("hit", False))
    probe_correct = bool(probe.get_state("hit", False))
    data.update(
        prime_response=prime.get_state("response", None),
        prime_rt=prime.get_state("rt", None),
        prime_correct=prime_correct,
        prime_timed_out=prime.get_state("response", None) is None,
        probe_response=probe.get_state("response", None),
        probe_rt=probe.get_state("rt", None),
        probe_correct=probe_correct,
        probe_timed_out=probe.get_state("response", None) is None,
        pair_correct=prime_correct and probe_correct,
    )
    return data
