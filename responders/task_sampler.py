from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    error_rate: float = 0.12
    timeout_rate: float = 0.03
    base_rt_s: float = 0.55
    negative_priming_cost_s: float = 0.04

    def __post_init__(self) -> None:
        self._rng: Any = None

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, feedback: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def act(self, observation: Observation) -> Action:
        keys = [str(value) for value in observation.valid_keys]
        if not keys:
            return Action(key=None, rt_s=None)
        if observation.phase not in {"prime_response", "probe_response"}:
            return Action(key="space" if "space" in keys else keys[0], rt_s=0.05)

        roll = float(self._rng.random()) if self._rng is not None else 1.0
        if roll < self.timeout_rate:
            return Action(key=None, rt_s=None)
        correct_key = str(observation.task_factors.get(f"{observation.phase.split('_')[0]}_correct_key", keys[0]))
        key = correct_key
        if roll < self.timeout_rate + self.error_rate:
            alternatives = [value for value in keys if value != correct_key]
            key = alternatives[0] if alternatives else correct_key
        jitter = float(self._rng.uniform(-0.06, 0.06)) if self._rng is not None else 0.0
        cost = self.negative_priming_cost_s if observation.phase == "probe_response" and observation.condition_id == "negative_priming" else 0.0
        return Action(key=key, rt_s=max(0.12, self.base_rt_s + cost + jitter))

