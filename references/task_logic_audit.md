# Task Logic Audit: Negative Priming

## 1. Paradigm Intent

- Task: Identity Negative Priming, shape-matching variant.
- Primary construct: selective attention to a target while suppressing a concurrent distractor, indexed by later slowing when that distractor becomes the target.
- Manipulated factors: prime distractor presence and prime-to-probe role relation (`no_distractor`, `control`, `negative_priming`).
- Dependent measures: probe accuracy, correct probe reaction time, and the negative-priming score (median correct probe RT for `negative_priming` minus `control`).
- Key citations: Friedman and Miyake (2004; P1) for the implemented shape-matching protocol; Kane et al. (1997; P2), Fox (1995; P3), and Frings et al. (2015; P4) for modal parameters, mechanism, and interpretation.

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 4 experimental blocks.
- Trials per block: 42 prime-probe pairs, for 168 pairs total, matching P1.
- Practice: 36 prime-probe pairs, matching P1.
- Randomization/counterbalancing: each experimental block contains 14 pairs of each condition. Shape identity, prime/probe match response, and left-side target/distractor assignments are deterministically randomized from the block seed. Current-pair shapes do not repeat in the next pair's prime assignment.
- Condition weight policy: custom generation fixes equal counts; `task.condition_weights` is omitted because weighted label scheduling cannot assign the required prime/probe item relations.
- Condition generation method: custom `generate_prime_probe_pairs(...)` in `src/utils.py`.
  - Simple labels cannot express that the prime distractor must become the probe target only in `negative_priming`, while all four probe/prime identities must be unrelated in `control`.
  - The generator returns a frozen, hashable `PrimeProbePair` dataclass containing `condition_id`, prime and probe target/distractor/reference shape IDs, correct keys, match flags, and pair index; `src/utils.py` owns the single dataclass-to-plan decoder.
- Runtime-generated trial values: none. Core factors and item identities are fixed before `run_trial()` and passed through `condition`.

### Trial State Machine

1. `ready`
   - Onset trigger: `ready` (10).
   - Stimuli shown: blue Chinese readiness prompt.
   - Valid keys: `space`.
   - Timeout behavior: none; participant controls pair onset.
   - Next state: `pre_pair_blank`.
2. `pre_pair_blank`
   - Onset trigger: `pre_pair_blank` (11).
   - Stimuli shown: black blank screen.
   - Duration: 1.100 s (P1).
   - Next state: `prime_fixation`.
3. `prime_fixation`
   - Onset trigger: `prime_fixation` (20).
   - Stimuli shown: white central fixation cross.
   - Duration: 0.500 s (P1).
   - Next state: `prime_response`.
4. `prime_response`
   - Onset trigger: condition-specific prime code (30-32).
   - Stimuli shown: left green target outline, optional overlapping red distractor outline, and right white reference outline.
   - Valid keys: `f` for different, `j` for same.
   - Timeout behavior: after the inferred 5.000 s implementation ceiling, record timeout and continue.
   - Next state: `inter_display_blank`.
5. `inter_display_blank`
   - Onset trigger: `inter_display_blank` (40).
   - Stimuli shown: black blank screen.
   - Duration: 0.100 s (P1 method text).
   - Next state: `probe_fixation`.
6. `probe_fixation`
   - Onset trigger: `probe_fixation` (50).
   - Stimuli shown: white central fixation cross.
   - Duration: 0.500 s (P1).
   - Next state: `probe_response`.
7. `probe_response`
   - Onset trigger: condition-specific probe code (60-62).
   - Stimuli shown: left green target outline superimposed on a red distractor outline, plus a right white reference outline.
   - Valid keys: `f` for different, `j` for same.
   - Timeout behavior: after the inferred 5.000 s implementation ceiling, record timeout and end the pair.
   - Next state: next pair's `ready` or block break.

## 3. Condition Semantics

- Condition ID: `no_distractor`
  - Participant-facing meaning: prime left target appears without a red distractor; the probe contains unrelated target and distractor shapes.
  - Concrete stimulus realization: green target outline on the left, white reference on the right; probe adds an overlapping red distractor.
  - Outcome rules: match/different decision is based only on green target versus white reference.
- Condition ID: `control`
  - Participant-facing meaning: both displays contain target and distractor, but no prime identity repeats in the probe.
  - Concrete stimulus realization: green-over-red left pair plus white right reference on prime and probe.
  - Outcome rules: match/different decision is based only on green target versus white reference.
- Condition ID: `negative_priming`
  - Participant-facing meaning: the ignored red shape in the prime becomes the green target in the probe.
  - Concrete stimulus realization: prime red distractor identity is redrawn in green as the probe target; a new red probe distractor and white reference accompany it.
  - Outcome rules: match/different decision is based only on current green target versus white reference.
- Participant-facing text source: `config/*.yaml` stimuli; shape vertices and colors are config-defined and rendered by `src/utils.py`.
- Auditability rationale: localization and perceptual values can be changed without changing trial orchestration.
- Localization strategy: Chinese copy and SimHei are in config; abstract shapes require no translation.

## 4. Response and Scoring Rules

- Response mapping: `f` = different, `j` = same.
- Response key source: `task.response_keys` in config.
- Missing-response policy: record timeout, incorrect response, and null RT; continue to the next phase/pair.
- Correctness logic: the chosen key matches whether the green target shape identity equals the white reference shape identity for that display.
- Reward/penalty updates: none.
- Running metrics: block accuracy and overall accuracy; final summary also reports the negative-priming RT contrast when both cells contain valid correct probe trials.
- Analysis exclusion: the primary RT contrast uses only pairs with correct, non-timeout prime and probe responses, following P1/P2 error-exclusion logic.

## 5. Stimulus Layout Plan

- Screen name: prime/probe shape-matching display.
- Stimulus IDs shown together: green target, optional red distractor, white reference.
- Layout anchors (`pos`): target/distractor centered at `[-3.8, 0]`; reference centered at `[3.8, 0]`; the target is drawn after the distractor so green lines occlude red lines, as specified by P1.
- Size/spacing: each abstract outline fits a 3.6 x 3.6 degree box; centers are separated by 7.6 degrees with the screen midpoint left clear.
- Readability/overlap checks: red/green overlap is intentional within the left stimulus; the reference is spatially isolated. Line width is 4 px equivalent and shapes remain within the 1280 x 800 field.
- Rationale: reference-aligned left comparison object and right reference object, with no response labels repeated on every trial.

## 6. Trigger Plan

- Experiment start/end: 1 / 99.
- Block start/end: 2 / 3.
- Ready and pre-pair blank: 10 / 11.
- Prime fixation: 20.
- Prime onsets: no distractor 30, control 31, negative priming 32.
- Prime responses: different 33, same 34, timeout 35.
- Inter-display blank: 40.
- Probe fixation: 50.
- Probe onsets: no distractor 60, control 61, negative priming 62.
- Probe responses: different 63, same 64, timeout 65.

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: one simple mode-aware flow with explicit practice and block loops.
- Manual event exception: the `ready` onset uses `trigger_runtime.send(...)` because PsyFlow's participant-paced `wait_and_continue()` primitive has no onset-trigger argument; response, timeout, and all timed phase events remain on StimUnit paths.
- `utils.py` used?: yes.
- Exact purpose: deterministic cross-stage pair generation, abstract-shape construction, and summary statistics.
- Custom controller used?: no; the task has no adaptive state.
- Custom generator rationale: item-level identity constraints span prime and probe displays and cannot be represented by condition labels alone.
- Legacy/backward-compatibility fallback logic required?: no.

## 8. Inference Log

- Decision: 5.000 s response ceiling.
  - Why inference was required: P1 states that displays remain until response and gives no finite deadline; QA/simulation and unattended runtime require a bounded window.
  - Citation-supported rationale: the ceiling preserves participant-paced responding while preventing indefinite hangs; it does not change valid-key or correctness semantics.
- Decision: 4 blocks of 42 pairs.
  - Why inference was required: P1 specifies 168 pairs but does not prescribe the runtime block partition in the method passage.
  - Citation-supported rationale: equal 14/14/14 condition counts per block preserve the exact overall 56/56/56 balance and permit rest breaks.
- Decision: eight newly constructed irregular closed outlines.
  - Why inference was required: P1 identifies eight abstract shapes and shows examples but does not publish reusable vector coordinates for the complete set.
  - Citation-supported rationale: the shapes preserve identity uniqueness, outline-only drawing, size, color roles, overlap, and occlusion rules without substituting semantic icons.
- Decision: Chinese instructions with `f`/`j` keyboard responses.
  - Why inference was required: the source used an English readiness cue and physical left/right buttons.
  - Citation-supported rationale: translation changes no nonverbal stimulus or match/mismatch rule; `f`/`j` preserve spatial left/right mapping.

## Contract Note

- Participant-facing labels, instructions, and options are config-defined.
- `src/run_trial.py` contains only state orchestration and no participant wording or item generation.
