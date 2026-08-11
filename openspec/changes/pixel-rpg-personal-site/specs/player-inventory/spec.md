## Status

**DISCUSSION** — 2026-08-11 用户提案；与 `agent-life` 的 `inventory_items` 统一扩展；见 `discussion-log.md` §D。

## ADDED Requirements

### Requirement: Backpack and home chest storage

Each adventurer SHALL have:

- **Backpack** (背包): items carried into dungeons and usable in the big world per item rules.
- **Home chest** (家里箱子 / 仓库): items stored at `/home`, not automatically taken into dungeons unless moved to backpack.

Item placement SHALL be server-authoritative (`location`: `backpack` | `home_chest`).

#### Scenario: Move item to backpack before dungeon

- **WHEN** an adventurer moves an item instance from home chest to backpack before entering a dungeon
- **THEN** the item is available for dungeon use subject to script and item rules

#### Scenario: Chest items not in dungeon by default

- **WHEN** an adventurer enters a dungeon with items only in home chest
- **THEN** those items are not available in the dungeon run inventory

### Requirement: Item instances with player-authored description

The system SHALL represent loot and shop goods as **item instances** with a catalog `item_def_id` plus optional **player-supplemented description** text editable by the owner.

#### Scenario: Open item in backpack

- **WHEN** the owner opens an item in the backpack UI
- **THEN** they may view catalog description and edit or append their personal description field

#### Scenario: Open item in home chest

- **WHEN** the owner opens an item in the home chest UI
- **THEN** the same personal description editing is available as in backpack

#### Scenario: Description change logged

- **WHEN** the owner saves a personal description change on an item instance
- **THEN** the update persists and an entry is written to `player_behavior_log` with event type `item_description_edit`

### Requirement: Item evaluation on obtain

When an adventurer obtains a new item instance (shop, dungeon loot, grant), the system MAY prompt them to submit an **evaluation** (评价) — free-text opinion of the item. Evaluations SHALL be persisted and logged.

#### Scenario: Submit evaluation after obtain

- **WHEN** the owner submits an evaluation for a newly obtained item instance
- **THEN** the text is stored linked to the item instance and logged as `item_review`

#### Scenario: Skip evaluation

- **WHEN** the owner dismisses the evaluation prompt
- **THEN** no evaluation is stored and obtain flow completes normally

### Requirement: Soul potion use actions separated

`soul_potion` SHALL support distinct server actions: **apply to eligible `object` creation** (awakening) vs **misuse drink**. Drinking MUST NOT awaken a creation.

#### Scenario: Apply potion to static object

- **WHEN** the owner uses soul potion with explicit apply-to-creation on `kind=object`
- **THEN** the awakening flow starts per `agent-life`

#### Scenario: Misdrink soul potion

- **WHEN** the owner uses soul potion with drink action (or equivalent misuse)
- **THEN** one potion is consumed, immediate SAN loss and `misdrink_frail_mind` debuff (3 days, 2× SAN loss rate) apply per `sanity-action-points`, the event is logged as `soul_potion_misdrink`, and daily AP rules apply to recovery actions

#### Scenario: Cannot drink potion to awaken creature

- **WHEN** the owner attempts to apply soul potion to `kind=creature`
- **THEN** the action is rejected without consuming the potion
