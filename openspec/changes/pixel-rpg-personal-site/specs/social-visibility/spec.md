## ADDED Requirements

### Requirement: Unified canSee function

The system SHALL implement a single `canSee(viewer, target)` function used by map presence, chat, gallery, online lists, and **bounty board taker display**. When `viewer` has `is_admin=true`, `canSee(viewer, target)` SHALL return true for all adventurers.

For non-admin adventurers, `canSee(A,B)` SHALL return true when **any** of:

1. A and B belong to the **same party** and neither is blocked (Creator-assigned bulk visibility), OR
2. A and B have a **mutual acquaintance link** in `user_acquaintances` (player-created via tavern grilled duck-heart ritual per `world-tavern`, or Creator-created via admin)

Otherwise `canSee(A,B)` returns false.

#### Scenario: Same party members

- **WHEN** two users belong to the same party and neither is blocked
- **THEN** `canSee(A,B)` and `canSee(B,A)` return true

#### Scenario: Different party members without acquaintance

- **WHEN** two users belong to different parties and have no mutual `user_acquaintances` link
- **THEN** `canSee(A,B)` returns false

#### Scenario: Mutual tavern acquaintance across parties

- **WHEN** A and B completed the grilled duck-heart ritual and are in different parties
- **THEN** `canSee(A,B)` and `canSee(B,A)` return true

### Requirement: Player-initiated acquaintance only via tavern ritual

Adventurers MUST NOT create mutual acquaintance links through any player-facing action other than the tavern grilled duck-heart ritual in `world-tavern`. The Creator MAY create or remove acquaintance links and party assignments in admin.

#### Scenario: No self-service acquaintance outside tavern

- **WHEN** an adventurer attempts an API to add an acquaintance without tavern ritual or admin role
- **THEN** the request is rejected with 403

### Requirement: Default party for new users

New adventurers created by the Creator SHALL be assigned to a default party. To support stranger-by-default social play with player-driven tavern acquaintance, the default SHOULD be a **solo party per user** (one adventurer per party) unless the Creator explicitly assigns a shared party. Legacy manifest name **「主世界」** MAY remain for Creator-bulk groups but MUST NOT auto-include all users if tavern acquaintance is enabled.

#### Scenario: New user solo default party

- **WHEN** the Creator creates a user without specifying a party and solo-default is configured
- **THEN** the user is the sole member of a new or assigned solo party and sees no other adventurers until acquaintance or Creator reassignment

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

When `canSee(viewer, target)` is false, the system SHALL NOT expose target's user id, display name, or character sprite to the viewer via map, chat APIs, or gallery — **except** while both are seated at the same tavern table per `world-tavern`, where display names MAY appear only in the table seating/chat UI.

#### Scenario: Gallery API cross-party

- **WHEN** user A requests gallery entries and user B is in another party
- **THEN** user B is not included in the response

#### Scenario: Presence API cross-party

- **WHEN** user A is on `/world` and user B is in another party
- **THEN** user A's client never receives user B's spawn packets

#### Scenario: Bounty board taker anonymous to stranger

- **WHEN** user A opens the bounty board and user B in another party has taken a slot
- **THEN** the slot shows an anonymous taker label and does not expose B's user id or display name

#### Scenario: Bounty board taker visible to acquaintance

- **WHEN** user A opens the bounty board and user C shares a mutual acquaintance link with A
- **THEN** the slot shows C's display name
