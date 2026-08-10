## ADDED Requirements

### Requirement: Revival platform in big world

The big world SHALL include a revival platform (复活台) interactable. Dead adventurers SHALL be directed there after dungeon death to restore their body.

#### Scenario: Sent to revival platform on death

- **WHEN** an adventurer dies in a dungeon
- **THEN** the client navigates to `/world` at the revival platform scene/spawn with dead status

#### Scenario: Living adventurer at revival platform

- **WHEN** a non-dead adventurer interacts with the revival platform
- **THEN** an informational message is shown and no roll or payment occurs

### Requirement: Revival cost by d100 roll

Revival cost SHALL be determined by a server-side d100 roll when the dead adventurer initiates revival at the platform. The cost MUST NOT be a fixed config-only price without rolling.

#### Scenario: Roll revival cost

- **WHEN** a dead adventurer opens the revival flow at the platform
- **THEN** the server rolls 1–100 and computes a revival gold cost from the shared revival cost formula

#### Scenario: Pay rolled cost and revive

- **WHEN** a dead adventurer confirms revival and wallet gold is greater than or equal to the rolled cost
- **THEN** gold is deducted by the rolled amount, `hp` is restored to `max_hp`, and `is_dead` is cleared

#### Scenario: Insufficient gold after roll

- **WHEN** a dead adventurer's wallet gold is less than the rolled revival cost
- **THEN** revival is not completed and the UI offers selling creations to raise gold

### Requirement: Sell creations to fund revival

When revival gold is insufficient, the dead adventurer SHALL be able to sell owned creations for gold after d100 appraisal and explicit confirmation.

#### Scenario: Appraise creation at revival

- **WHEN** a dead adventurer requests appraisal for an owned creation at the revival platform
- **THEN** the server rolls 1–100 and computes a sell offer value from the appraisal formula

#### Scenario: Confirm sell after appraisal

- **WHEN** the adventurer confirms selling an appraised creation
- **THEN** the creation is deleted (and removed from home placements), and the appraised gold is added to wallet gold

#### Scenario: Decline sell after appraisal

- **WHEN** the adventurer declines selling after seeing an appraised value
- **THEN** the creation remains owned and no gold is added

### Requirement: One appraisal per creation per hour

The system SHALL allow at most one appraisal roll per creation per rolling 60-minute window. Repeated appraisal attempts within the window MUST be rejected.

#### Scenario: Appraisal cooldown active

- **WHEN** an adventurer attempts to re-appraise the same creation within 60 minutes of the last appraisal
- **THEN** the system returns a cooldown error with remaining time themed copy

#### Scenario: Appraisal after cooldown

- **WHEN** 60 minutes have passed since the last appraisal of a creation
- **THEN** a new appraisal roll is permitted

### Requirement: Dead state restrictions

While dead, adventurers MUST NOT enter dungeons until revived at the revival platform.

#### Scenario: Block dungeon entry when dead

- **WHEN** a dead adventurer attempts a dungeon entrance
- **THEN** entry is blocked with guidance to the revival platform
