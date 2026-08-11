## Status

**DISCUSSION** — 2026-08-11 用户提案；细节见 `discussion-log.md` §D。

## ADDED Requirements

### Requirement: Church location in big world

The system SHALL provide a **church** (教堂) accessible from `/world` via a registered scene interactable (e.g., `church_entrance` or dedicated scene `shrine-church`). Authenticated adventurers with world access MAY enter to confess.

#### Scenario: Enter church from world

- **WHEN** an adventurer interacts with the church entrance in the big world
- **THEN** a church UI opens with confession (留言板-style) and themed copy

#### Scenario: Church requires login

- **WHEN** an unauthenticated user attempts church APIs
- **THEN** access is denied by the login wall

### Requirement: Confession message board

The church SHALL expose a confession board where adventurers MAY post confession text (similar to a message board). Confessions SHALL be persisted and appended to `player_behavior_log` with event type `church_confession`.

#### Scenario: Submit confession

- **WHEN** an adventurer submits non-empty confession text within configured length limits
- **THEN** the confession is stored, visible per visibility rules (see discussion §D), and logged for Truth Eye processing

#### Scenario: Confession grants trait increase

- **WHEN** a confession is successfully submitted and cooldown/rules pass
- **THEN** the server applies a configured **trait / attribute increase** (e.g., piety or an `attrs` field) and logs the adjustment

#### Scenario: Confession cooldown

- **WHEN** an adventurer attempts to confess again before cooldown expires
- **THEN** the request is rejected with themed feedback and no additional trait bonus

### Requirement: Confession visibility

Confession display visibility SHALL be configurable (e.g., public to all logged-in adventurers, acquaintances only, or Creator-only board). Default SHALL be documented in `design.md` when decided.

#### Scenario: Public confession board

- **WHEN** visibility is public and an adventurer opens the church board
- **THEN** recent confessions from other adventurers are listed per pagination rules
