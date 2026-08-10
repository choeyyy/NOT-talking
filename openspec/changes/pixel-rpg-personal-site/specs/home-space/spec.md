## ADDED Requirements

### Requirement: Home tab for logged-in adventurers

The system SHALL provide a `/home` tab as the personal home space for authenticated adventurers. Users not on `/world` SHALL be able to remain online at home after login.

#### Scenario: Login lands at home

- **WHEN** an adventurer logs in successfully
- **THEN** the system redirects to `/home` by default

### Requirement: Dual entry for creation and placement

The system SHALL expose creation management via `/workshop` and home placement via `/home` cabinet drag-and-drop. Both views SHALL reflect the same underlying `creations` data.

#### Scenario: Edit in workshop reflects at home

- **WHEN** the owner updates a creation description in `/workshop`
- **THEN** the updated description appears on hover for that item placed in `/home`

#### Scenario: Shortcut to workshop from home

- **WHEN** the owner clicks a themed link or button from the home cabinet (e.g., "造物")
- **THEN** the app navigates to `/workshop` for full creation editing

### Requirement: Phone interaction for online chat

The home space SHALL include an interactive phone object. Interacting with the phone SHALL open a list of online mutual acquaintances (per `canSee`) whom the user may message in real time.

#### Scenario: Open phone contact list

- **WHEN** a user interacts with the phone at home
- **THEN** a list of currently online acquaintances is shown with their presence label (e.g., at home or in world scene)

#### Scenario: Start chat from phone

- **WHEN** a user selects an online acquaintance from the phone list
- **THEN** a live chat dialog opens and messages may be exchanged per `player-chat` rules

#### Scenario: No online acquaintances

- **WHEN** a user opens the phone and no mutual acquaintances are online
- **THEN** an empty-state message is shown in themed copy

### Requirement: Home presence without world sprite

Users on `/home` SHALL register online presence with context `home` and MUST NOT appear as map sprites on `/world`.

#### Scenario: User at home not on world map

- **WHEN** user A is on `/home` and user B is on `/world` in the same scene
- **THEN** user B's world map does not render user A's sprite

#### Scenario: Creator sees home presence

- **WHEN** the Creator views the global online list
- **THEN** adventurers on `/home` appear with an at-home label

#### Scenario: User switches to home tab

- **WHEN** an authenticated user opens `/home`
- **THEN** a pixel-styled home scene is displayed with cabinet, draggable placements, and phone

### Requirement: Place creations via drag from home cabinet

The owner SHALL place owned creations by dragging from the home cabinet onto the room canvas. Placement data SHALL be stored in `home_config` with creation id and coordinates.

#### Scenario: Drag placement

- **WHEN** the owner drags a creation from the cabinet and drops it on the room canvas
- **THEN** the item appears at the drop position when viewing `/home`

#### Scenario: Place from workshop without drag

- **WHEN** the owner uses a non-drag placement control (optional fallback)
- **THEN** the item may also be placed at a default or selected position

#### Scenario: Remove placement

- **WHEN** the owner removes a placed item from the home room
- **THEN** the item remains in the cabinet inventory but is no longer rendered in the room

### Requirement: Hover description tooltip

Placed home items and cabinet previews SHALL show the creation's description in a tooltip on mouse hover.

#### Scenario: Hover placed object

- **WHEN** the owner hovers over a placed creation in the home room
- **THEN** a tooltip displays the creation's description text

### Requirement: Random creature speech at home

Placed creatures (`kind=creature`) SHALL periodically display a JRPG-style speech bubble containing a randomly selected phrase from the owner's configured list while the owner is viewing `/home`.

#### Scenario: Creature speaks randomly

- **WHEN** a placed creature has phrases configured and the owner is on `/home`
- **THEN** the client occasionally shows a speech bubble with one randomly chosen phrase

#### Scenario: Static object does not speak

- **WHEN** a placed creation has kind `object`
- **THEN** no random speech bubbles are shown

### Requirement: Home decoration extensibility

The system SHALL store home layout in `home_config` JSON including placements and future decorative fields (wallpaper, furniture templates).

#### Scenario: New user home config

- **WHEN** a new adventurer account is created
- **THEN** `home_config` defaults to empty placements and a starter room template
