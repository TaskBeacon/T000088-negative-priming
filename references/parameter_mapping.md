# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `total_pairs` | `task.total_trials` | `168` | `P1` | Methods: tasks comprised 168 prime-probe pairs. | `direct` | Four blocks of 42 preserve total and balance. |
| `practice_pairs` | `task.practice_trials` | `36` | `P1` | Methods: participants completed 36 practice prime-probe pairs. | `direct` | Practice represents all three conditions. |
| `condition_counts` | `task.conditions` | `56 each` | `P1` | 56 no-distractor primes, 56 control probes, and 56 negative-priming probes. | `direct` | Custom generator fixes equal counts. |
| `ready_blank` | `timing.ready_blank_duration` | `1.100 s` | `P1` | Ready button was followed by a blank screen for 1,100 ms. | `direct` | Starts after SPACE. |
| `fixation` | `timing.fixation_duration` | `0.500 s` | `P1` | Fixation point appeared for 500 ms before prime and probe. | `direct` | Same duration for both displays. |
| `inter_display` | `timing.inter_display_duration` | `0.100 s` | `P1` | After the prime response, the screen was blank for 100 ms. | `direct` | Black blank display. |
| `response_deadline` | `timing.response_timeout` | `5.000 s` | `P1` | Source display remained until response. | `inferred` | Bounded runtime ceiling; responses terminate immediately. |
| `target_color` | `task.colors.target` | `#00C853` | `P1` | Target shape was green. | `adapted` | High-luminance green for black background. |
| `distractor_color` | `task.colors.distractor` | `#EF4444` | `P1` | Distractor shape was red. | `adapted` | High-luminance red for black background. |
| `reference_color` | `task.colors.reference` | `#FFFFFF` | `P1` | Reference shape was white. | `direct` | Outline-only. |
| `left_position` | `task.layout.left_pos` | `[-3.8, 0]` | `P1` | Target/distractor appeared left of fixation and reference right of fixation. | `adapted` | Degree-unit position preserves clear separation. |
| `right_position` | `task.layout.right_pos` | `[3.8, 0]` | `P1` | Shape centers were symmetrically placed around fixation. | `adapted` | Degree-unit counterpart to left position. |
| `shape_extent` | `task.layout.shape_scale` | `1.8` | `P1` | Each shape was approximately 1.5 inches square at the cited setup. | `adapted` | Visual-degree scaling for configured monitor. |
| `response_keys` | `task.response_keys` | `{different: f, same: j}` | `P1` | Left button indicated mismatch; right button indicated match. | `adapted` | Standard keyboard spatial equivalents. |
| `primary_score` | analysis summary | `median RT(NP) - median RT(control)` | `P1` | NP effects were the RT difference between negative-priming and control-distractor probes. | `direct` | Correct prime/probe pairs only. |

