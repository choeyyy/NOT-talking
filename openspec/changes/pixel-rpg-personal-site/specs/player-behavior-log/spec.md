## Status

**DISCUSSION** — 2026-08-11 用户提案；为 **真理之眼** 与 **档案地精** 提供输入；见 `discussion-log.md` §D。

## ADDED Requirements

### Requirement: Unified player behavior log

The system SHALL persist a unified **`player_behavior_log`** for each adventurer with server-side events including at minimum:

| event_type | Source |
|------------|--------|
| `item_review` | Item evaluation on obtain |
| `item_description_edit` | Personal description edit on item instance |
| `dungeon_choice` | Dungeon branch / option selection (may reference `dungeon_run_log`) |
| `church_confession` | Church confession submit |
| `shop_purchase` | World shop buy |
| `soul_potion_misdrink` | Soul potion drunk instead of applied |
| `library_read` | Library read session |
| `library_disturbing_book` | Disturbing book SAN loss during library |
| `home_sleep` | Sleep at home (debuff recovery) |
| `san_change` | Notable SAN delta audit (optional aggregate) |
| `ap_spent` | Daily action point spend (optional aggregate) |
| `ap_dice_use` | Action point dice used; AP gained |
| `gnome_guild_rejection` | Adventurer turned away at world gnome guild entrance |
| `bounty_accept` | Bounty board accept; AP spent |
| `bounty_settle` | Bounty mini-run completion; gold delta |
| `tavern_food_purchase` | Duck heart / tavern menu buy |
| `tavern_sit_invite` | Sit-together invite sent or responded |
| `tavern_duck_heart_eaten` | Duck heart consumed; payload includes `eat_context` (`bond_ritual` \| `solo`) and stat deltas |
| `acquaintance_formed` | Mutual `user_acquaintances` link created (tavern ritual or admin) |

Each row SHALL include `user_id`, `event_type`, `payload` JSON, and `created_at`.

#### Scenario: Shop purchase logged

- **WHEN** an adventurer completes a shop purchase
- **THEN** a `shop_purchase` log entry records item id, price, and resulting inventory change

#### Scenario: Dungeon choice logged

- **WHEN** an adventurer selects a dungeon script choice at a branch node
- **THEN** a `dungeon_choice` entry records run id, node id, and choice id (in addition to any `dungeon_run_log` telemetry)

#### Scenario: Adventurers cannot read full behavior log

- **WHEN** a non-admin adventurer requests behavior log history API
- **THEN** the server returns 403 or an allowed summary only per product rules

#### Scenario: Creator audits behavior log

- **WHEN** the Creator opens admin audit for an adventurer
- **THEN** persisted behavior log entries are readable in chronological order

### Requirement: Cross-link dungeon telemetry

`dungeon_run_log` (dice, hp/gold deltas, settlements) and `player_behavior_log` (`dungeon_choice`) SHALL share `run_id` / `dungeon_id` references where applicable so Truth Eye and archivist tools can correlate narrative choices with outcomes.

#### Scenario: Choice linked to run

- **WHEN** a dungeon choice is logged
- **THEN** the payload includes `run_id` matching the active `dungeon_runs` record
