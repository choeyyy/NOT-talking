## Status

**DISCUSSION** — 2026-08-11 用户提案；见 `discussion-log.md` §D。

## ADDED Requirements

### Requirement: Truth Eye reads behavior logs

The system SHALL provide **真理之眼** (Truth Eye) — a world feature (UI entry in big world and/or periodic server job) that reads an adventurer's **`player_behavior_log`** (and permitted aggregates from `dungeon_run_log`) and **adjusts persistent `attrs`** up or down according to configured or AI-assisted rules.

#### Scenario: Truth Eye session adjusts attrs

- **WHEN** an adventurer invokes Truth Eye or a scheduled evaluation runs after new log activity
- **THEN** the server computes attribute deltas from log analysis, applies them to wallet `attrs`, and logs `truth_eye_adjustment` events with before/after snapshot

#### Scenario: Adjustment audit

- **WHEN** Truth Eye changes attributes
- **THEN** each change is persisted in `player_behavior_log` with reason summary in payload for Creator audit

### Requirement: Attributes affect dungeon and loot probability

Persistent `attrs` (including traits modified by church confession and Truth Eye) SHALL influence dungeon check resolution and loot/drop probabilities. The server SHALL document modifier formulas in `design.md` when implemented.

#### Scenario: Attr modifier on d100 check

- **WHEN** Truth Eye or church has changed an adventurer's attrs used by a dungeon script check
- **THEN** subsequent dungeon checks use the updated wallet attrs per shared resolver rules

### Requirement: Truth Eye distinct from oracle and gnome guild

Truth Eye SHALL be a dedicated product surface (rules engine and/or bounded AI summary over logs), separate from the global **oracle** tool and **Gnome Guild** agents, though it MAY use the same Cursor API proxy with a different system prompt.

#### Scenario: Oracle does not mutate attrs

- **WHEN** an adventurer uses the floating oracle chat
- **THEN** wallet attrs are not changed by oracle responses alone without Truth Eye pipeline
