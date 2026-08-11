## Status

**DISCUSSION** — 2026-08-11 用户提案；见 `sanity-action-points`、`discussion-log.md` §E。

## ADDED Requirements

### Requirement: Library in big world

The system SHALL provide a **library** (图书馆) in `/world` via scene interactable or dedicated scene. Adventurers MAY visit to read and reduce `misdrink_frail_mind` debuff duration per `sanity-action-points`.

#### Scenario: Enter library from world

- **WHEN** an adventurer interacts with the library entrance
- **THEN** a library UI opens with read action costing daily AP

#### Scenario: Read blocked without AP

- **WHEN** an adventurer attempts to read with 0 daily AP remaining
- **THEN** the action is rejected

### Requirement: Probabilistic disturbing book

Each library read session SHALL have a configured probability of encountering a **SAN-draining book** (看到掉 SAN 的书). On trigger, the adventurer loses additional SAN beyond the normal read outcome.

#### Scenario: Normal read shortens debuff

- **WHEN** a read session completes without disturbing book trigger
- **THEN** misdrink debuff remaining duration decreases by configured amount and AP is spent

#### Scenario: Disturbing book triggers extra SAN loss

- **WHEN** the disturbing book roll succeeds during a read session
- **THEN** additional SAN is lost (base amount; doubled if `misdrink_frail_mind` active), the outcome is narrated in JRPG style, and `player_behavior_log` records `library_disturbing_book`

#### Scenario: Disturbing book still counts as read session

- **WHEN** disturbing book triggers
- **THEN** debuff duration reduction from that session still applies unless design configures otherwise

### Requirement: Library actions logged

All library read outcomes SHALL append to `player_behavior_log` with event type `library_read` or `library_disturbing_book`.

#### Scenario: Log includes roll outcome

- **WHEN** a library session completes
- **THEN** the log payload includes disturbing-book boolean, SAN delta, debuff duration delta, and AP spent
