## ADDED Requirements

### Requirement: Shop in big world

The system SHALL provide a shop accessible from the big world (`/world`) where adventurers spend persistent gold on configured items.

#### Scenario: Enter shop from world

- **WHEN** an adventurer interacts with the shop entrance or NPC in a world scene
- **THEN** a shop UI opens listing available items and prices

#### Scenario: Purchase item

- **WHEN** an adventurer buys an item with sufficient persistent gold
- **THEN** gold is deducted server-side and the purchase effect is applied (e.g., heal HP, add inventory item)

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
