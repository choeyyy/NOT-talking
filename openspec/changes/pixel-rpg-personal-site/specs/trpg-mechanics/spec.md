## ADDED Requirements

### Requirement: Persistent adventurer stats

Each adventurer SHALL have persistent `hp`, `max_hp`, `gold`, `attrs`, and `is_dead` stored server-side. Dungeons read and mutate wallet `hp` and `attrs`; dungeon runs track `dungeon_exp`.

#### Scenario: d100 uses attributes

- **WHEN** a check specifies a stat modifier from `attrs.str`
- **THEN** the server adjusts effective DC or tier resolution per script rules

#### Scenario: Enter dungeon with current wallet stats

- **WHEN** an adventurer starts or resumes a dungeon
- **THEN** gameplay uses current wallet `hp` and `attrs`, plus run `dungeon_exp`

#### Scenario: New adventurer stats

- **WHEN** a new adventurer account is created
- **THEN** default starting hp, max_hp, gold, and attrs are assigned per configuration

#### Scenario: Stats visible to owner

- **WHEN** an adventurer views the profile or sidebar HUD
- **THEN** current HP, gold, and attributes are displayed

### Requirement: d100 resolution rules

The system SHALL resolve d100 checks using configurable tier bands relative to a node DC. The default tier mapping SHALL be documented in `design.md` and applied consistently across dungeons unless a script overrides bands.

#### Scenario: Roll at DC 60

- **WHEN** a check with DC 60 is rolled and the result is 45
- **THEN** the outcome tier is computed by the shared resolver and applied

### Requirement: Server authoritative rolls and stat changes

All d100 rolls and HP/gold mutations during dungeons SHALL occur on the server. The client MUST NOT trust client-supplied roll values for outcomes.

#### Scenario: Client requests roll

- **WHEN** the client requests advancement on a roll node
- **THEN** the server rolls 1–100, applies effects, and returns narrative and updated stats
