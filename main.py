from __future__ import annotations

from contextlib import nullcontext
from functools import partial
from pathlib import Path

import pandas as pd
from psychopy import core
from psyflow import (
    BlockUnit,
    StimBank,
    StimUnit,
    SubInfo,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
)

from src.run_trial import run_trial
from src.utils import generate_prime_probe_pairs, summarize


MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def run(options):
    root = Path(__file__).resolve().parent
    config = load_config(str(options.config_path))
    output_dir, scope, context = None, nullcontext(), None
    if options.mode in ("qa", "sim"):
        context = context_from_config(task_dir=root, config=config, mode=options.mode)
        output_dir, scope = context.output_dir, runtime_context(context)

    with scope:
        if options.mode == "qa":
            subject = {"subject_id": "qa088"}
        elif options.mode == "sim":
            subject = {"subject_id": str(context.session.participant_id or "sim088")}
        else:
            subject = SubInfo(config["subform_config"]).collect()

        settings = TaskSettings.from_dict(config["task_config"])
        settings.add_subinfo(subject)
        if output_dir is not None:
            settings.save_path = str(output_dir)
        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")

        settings.triggers = config["trigger_config"]
        triggers = initialize_triggers(mock=True) if options.mode in ("qa", "sim") else initialize_triggers(config)
        win, kb = initialize_exp(settings)
        bank = StimBank(win, config["stim_config"]).preload_all()
        settings.save_to_json()
        triggers.send(settings.triggers.get("experiment_start"))

        StimUnit("instruction", win, kb, runtime=triggers).add_stim(bank.get("instruction_general")).wait_and_continue()

        rows: list[dict] = []
        practice = (
            BlockUnit(
                block_id="practice",
                block_idx=0,
                settings=settings,
                window=win,
                keyboard=kb,
                n_trials=int(settings.practice_trials),
                seed=int(settings.overall_seed) + 9000,
            )
            .generate_conditions(
                func=generate_prime_probe_pairs,
                n_trials=int(settings.practice_trials),
                condition_labels=list(settings.conditions),
                shape_ids=list(settings.shape_ids),
                response_keys=dict(settings.response_keys),
            )
            .run_trial(partial(run_trial, stim_bank=bank, trigger_runtime=triggers, block_id="practice", block_idx=0, is_practice=True))
        )
        practice.to_dict(rows)

        for block_index in range(int(settings.total_blocks)):
            block_number = block_index + 1
            StimUnit("block_start_screen", win, kb, runtime=triggers).add_stim(
                bank.get_and_format("block_start", block_number=block_number, total_blocks=int(settings.total_blocks))
            ).wait_and_continue()
            block_id = f"block_{block_number}"
            block = (
                BlockUnit(
                    block_id=block_id,
                    block_idx=block_index,
                    settings=settings,
                    window=win,
                    keyboard=kb,
                    n_trials=int(settings.trials_per_block),
                    seed=int(settings.block_seed[block_index]),
                )
                .generate_conditions(
                    func=generate_prime_probe_pairs,
                    n_trials=int(settings.trials_per_block),
                    condition_labels=list(settings.conditions),
                    shape_ids=list(settings.shape_ids),
                    response_keys=dict(settings.response_keys),
                )
                .on_start(lambda _, runtime=triggers: runtime.send(settings.triggers.get("block_start")))
                .on_end(lambda _, runtime=triggers: runtime.send(settings.triggers.get("block_end")))
                .run_trial(partial(run_trial, stim_bank=bank, trigger_runtime=triggers, block_id=block_id, block_idx=block_index, is_practice=False))
            )
            block_rows: list[dict] = []
            block.to_dict(block_rows)
            rows.extend(block_rows)
            if block_index < int(settings.total_blocks) - 1:
                block_accuracy = sum(bool(row.get("pair_correct")) for row in block_rows) / len(block_rows) if block_rows else 0.0
                StimUnit("block_break", win, kb, runtime=triggers).add_stim(
                    bank.get_and_format("block_break", block_number=block_number, accuracy=block_accuracy)
                ).wait_and_continue()

        summary = summarize(rows)
        StimUnit("good_bye", win, kb, runtime=triggers).add_stim(bank.get_and_format("good_bye", **summary)).wait_and_continue(terminate=True)
        triggers.send(settings.triggers.get("experiment_end"))
        pd.DataFrame(rows).to_csv(settings.res_file, index=False)
        triggers.close()
        core.quit()


def main():
    run(
        parse_task_run_options(
            task_root=Path(__file__).resolve().parent,
            description="Run the Negative Priming task",
            default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
            modes=MODES,
        )
    )


if __name__ == "__main__":
    main()

