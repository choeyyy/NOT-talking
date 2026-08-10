## ADDED Requirements

### Requirement: Unified canSee function

The system SHALL implement a single `canSee(viewer, target)` function used by map presence, chat, gallery, and online lists. When `viewer` has `is_admin=true`, `canSee(viewer, target)` SHALL return true for all adventurers.

#### Scenario: Same party members

- **WHEN** two users belong to the same party and neither is blocked
- **THEN** `canSee(A,B)` and `canSee(B,A)` return true

#### Scenario: Different party members

- **WHEN** two users belong to different parties
- **THEN** `canSee(A,B)` returns false

### Requirement: Creator chat bypass

The Creator SHALL bypass `canSee` restrictions for world-map omniscience, online lists, and chat initiation. Adventurers SHALL remain subject to `canSee` for map visibility, chat, and gallery.

#### Scenario: Creator perceives cross-party adventurer

- **WHEN** two adventurers are in different parties and both are online on `/world`
- **THEN** the Creator still receives both in the global online list and may locate and chat with either

### Requirement: Creator hidden from adventurer map presence

Adventurers SHALL NOT receive the Creator's map sprite or presence packets on `/world`. Creator omniscience is one-way for map rendering.

#### Scenario: Adventurer world tab without Creator sprite

- **WHEN** an adventurer is on `/world` and the Creator is also online on `/world`
- **THEN** the adventurer's map does not render the Creator's character sprite

### Requirement: Strangers invisible identifiers

When `canSee(viewer, target)` is false, the system SHALL NOT expose target's user id, display name, or character sprite to the viewer via map, chat APIs, or gallery.

#### Scenario: Gallery API cross-party

- **WHEN** user A requests gallery entries and user B is in another party
- **THEN** user B is not included in the response

#### Scenario: Presence API cross-party

- **WHEN** user A is on `/world` and user B is in another party
- **THEN** user A's client never receives user B's spawn packets

### Requirement: Default party for new users

New adventurers created by the Creator SHALL be assigned to a default party (e.g., "主世界") unless specified otherwise, making them mutually visible with same-party members.

#### Scenario: New user default party

- **WHEN** the Creator creates a user without specifying a party
- **THEN** the user is assigned to the default party
