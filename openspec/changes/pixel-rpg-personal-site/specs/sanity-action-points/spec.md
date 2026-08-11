## Status

**DISCUSSION** — 2026-08-11 用户提案；与误喝 debuff、行动点联动；见 `discussion-log.md` §D/E。

## ADDED Requirements

### Requirement: Sanity stat

Each adventurer SHALL have persistent **san** (理智 / SAN) and `max_san` stored server-side alongside other wallet stats. SAN loss and gain SHALL occur only on the server.

#### Scenario: SAN visible in HUD

- **WHEN** an adventurer views profile or sidebar HUD
- **THEN** current SAN and max SAN are displayed

#### Scenario: SAN at zero or below threshold

- **WHEN** SAN falls to a configured critical threshold
- **THEN** themed feedback or debuff effects apply per `design.md` (details TBD)

### Requirement: Misdrink soul potion SAN penalty

When an adventurer **misdrinks** soul potion (`soul_potion_misdrink`), the server SHALL:

1. Consume one `soul_potion`
2. Apply immediate **SAN loss** (amount configurable)
3. Apply debuff **`misdrink_frail_mind`** for **3 days** (72h or three daily resets — see `design.md`)

While `misdrink_frail_mind` is active, any SAN decrease SHALL be multiplied by **2×** relative to the base loss amount before debuff.

#### Scenario: Misdrink applies debuff

- **WHEN** an adventurer misdrinks soul potion
- **THEN** inventory decreases by one potion, SAN drops immediately, debuff is stored with expiry or remaining duration, and `player_behavior_log` records the event

#### Scenario: Doubled SAN loss under debuff

- **WHEN** a SAN loss event occurs while `misdrink_frail_mind` is active
- **THEN** the applied loss is twice the base loss (before clamping to min SAN)

### Requirement: Daily action points

Each adventurer SHALL have **daily action points** (AP) that reset on a configured calendar boundary (e.g., UTC+8 midnight). The default daily maximum SHALL be **28 AP** per adventurer. Actions that consume real progression time SHALL cost AP including at minimum:

| Action | Typical cost (configurable) |
|--------|----------------------------|
| Enter / continue dungeon run step | 1+ AP |
| Accept bounty at bounty board | 1 AP (default) |
| Read at library | 1 AP |
| Sleep at home | 1 AP |
| (others as added) | per manifest |

#### Scenario: Action blocked when AP exhausted

- **WHEN** an adventurer has 0 remaining AP for the current day
- **THEN** AP-costing actions (library, sleep, new dungeon entry, etc.) are rejected with themed feedback

#### Scenario: Daily AP reset

- **WHEN** a new daily period begins
- **THEN** remaining AP resets to **28** (or configured daily maximum)

#### Scenario: Default daily AP is 28

- **WHEN** an adventurer's daily AP is initialized for a new period
- **THEN** remaining AP equals 28 unless modified by prior carry rules (none in V1)

#### Scenario: AP prevents infinite debuff grinding

- **WHEN** an adventurer has spent all daily AP
- **THEN** they cannot repeat library or sleep actions until the next reset even if debuff remains

### Requirement: Action point dice from shop

When daily AP is insufficient, adventurers MAY obtain more AP by purchasing **action point dice** (行动点数色子) from the big-world shop per `world-shop`. Each dice use SHALL grant a **random integer from 0 to 5 inclusive** added to **remaining daily AP** for the current period.

#### Scenario: Buy AP dice without spending AP

- **WHEN** an adventurer with 0 daily AP opens the shop and buys action point dice with sufficient gold and under the daily purchase limit
- **THEN** the purchase succeeds without requiring AP; gold is deducted and the dice item is added to inventory

#### Scenario: Use AP dice rolls 0 to 5

- **WHEN** an adventurer uses an action point dice from inventory during the current daily period
- **THEN** the server rolls uniformly (unless configured) in `[0, 5]`, adds that amount to remaining daily AP, consumes one dice, and logs the roll value

#### Scenario: Zero roll is valid

- **WHEN** an AP dice roll results in 0
- **THEN** no AP is added, the dice is still consumed, and the outcome is shown with themed copy

#### Scenario: AP dice does not bypass daily reset

- **WHEN** a new daily period begins
- **THEN** AP resets to the daily maximum; unused dice items remain in inventory unless expired by rules

### Requirement: Shop exempt from action point costs

Visiting the shop, browsing catalog, and purchasing items (including action point dice) SHALL **NOT** consume daily action points. The shop MUST remain accessible even when remaining AP is 0.

#### Scenario: Enter shop at zero AP

- **WHEN** an adventurer has 0 daily AP and interacts with the shop in `/world`
- **THEN** the shop UI opens normally

#### Scenario: Purchase at zero AP

- **WHEN** an adventurer buys any shop item including action point dice with 0 AP remaining
- **THEN** the purchase proceeds if gold and other rules pass; AP is not deducted for the shop transaction itself

### Requirement: Debuff duration reduction via library and sleep

While `misdrink_frail_mind` is active, the adventurer MAY reduce **remaining debuff duration** by:

- **Reading** at the big-world library (`world-library`) — costs AP
- **Sleeping** at home (`/home`) — costs AP

Each successful session SHALL shave configured time from the debuff (e.g., hours or fractional day). When remaining duration reaches zero, the 2× SAN loss multiplier ends.

#### Scenario: Library session shortens debuff

- **WHEN** an adventurer completes a library read action with sufficient AP
- **THEN** debuff remaining duration decreases by configured amount and AP decreases by configured cost

#### Scenario: Home sleep shortens debuff

- **WHEN** an adventurer completes a home sleep action with sufficient AP
- **THEN** debuff remaining duration decreases and AP decreases

### Requirement: Behavior logging for vitals actions

Misdrink, SAN changes, AP spend, library reads (including bad outcomes), and home sleep SHALL write entries to `player_behavior_log` for Truth Eye and Creator audit.

#### Scenario: Log library read

- **WHEN** an adventurer reads at the library
- **THEN** a log entry records outcome including any debuff duration change and SAN delta

#### Scenario: Log home sleep

- **WHEN** an adventurer sleeps at home
- **THEN** a log entry records debuff duration change and AP cost
