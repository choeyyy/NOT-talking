## ADDED Requirements

### Requirement: Shop in big world

The system SHALL provide a shop accessible from the big world (`/world`) where adventurers spend persistent gold on configured items.

#### Scenario: Enter shop from world

- **WHEN** an adventurer interacts with the shop entrance or NPC in a world scene
- **THEN** a shop UI opens listing available items and prices

#### Scenario: Purchase item

- **WHEN** an adventurer buys an item with sufficient persistent gold
- **THEN** gold is deducted server-side, the purchase effect is applied, and a `shop_purchase` entry is written to `player_behavior_log` per `player-behavior-log`

#### Scenario: Insufficient gold

- **WHEN** an adventurer attempts to buy an item costing more than their gold
- **THEN** the purchase is rejected with themed feedback

### Requirement: Shop catalog by manifest

Shop items SHALL be registered in a code manifest (`shop-manifest`) with id, name, description, price, and effect configuration. The Creator MAY update catalog via manifest deploy without adventurer-facing editors in V1.

#### Scenario: Display catalog item

- **WHEN** the shop UI loads
- **THEN** items from the manifest are listed with price and description

### Requirement: Gold spent only from persistent wallet

Shop purchases SHALL deduct from persistent wallet gold, not temporary dungeon run gold.

#### Scenario: Dungeon run gold not spendable

- **WHEN** an adventurer is mid-dungeon with run gold not yet merged
- **THEN** that gold is not available in the shop until the run completes successfully

### Requirement: Action point dice in shop catalog

The shop SHALL sell **action point dice** (行动点数色子) as a catalog item. Each adventurer MAY purchase at most **3** action point dice per daily period. Purchasing or using the dice SHALL follow `sanity-action-points` (random **0–5** AP per use).

#### Scenario: AP dice listed in shop

- **WHEN** the shop UI loads
- **THEN** action point dice appears with price, description, and remaining daily purchase quota (out of 3)

#### Scenario: Buy AP dice when AP exhausted

- **WHEN** an adventurer with 0 daily AP purchases action point dice with sufficient gold and fewer than 3 bought today
- **THEN** the purchase completes without AP cost for shop access

#### Scenario: Daily purchase limit enforced

- **WHEN** an adventurer already purchased 3 action point dice in the current daily period
- **THEN** further dice purchases are rejected until the next daily reset

#### Scenario: Purchase counter resets daily

- **WHEN** a new daily period begins
- **THEN** the action point dice purchase count resets to 0 and up to 3 may be bought again

### Requirement: Shop not gated by action points

Shop access and purchases SHALL NOT require or consume daily action points. This explicitly includes purchases made when AP is 0.

#### Scenario: Shop always reachable from world

- **WHEN** an adventurer interacts with the shop entrance regardless of daily AP balance
- **THEN** entry and transactions are allowed subject only to gold, login, and page-access rules
