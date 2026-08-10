## ADDED Requirements

### Requirement: Online presence contexts

The system SHALL track each connected adventurer's presence context as `home` or `world`. World context SHALL include `sceneId` and map coordinates. Home context SHALL NOT include world coordinates.

#### Scenario: User enters home tab

- **WHEN** a user opens `/home` with an active WebSocket
- **THEN** the server records presence context `home` and notifies eligible subscribers

#### Scenario: User enters world tab

- **WHEN** a user opens `/world` and joins a scene room
- **THEN** the server records presence context `world` with scene and coordinates

#### Scenario: User leaves social tabs

- **WHEN** a user navigates to a non-social tab (e.g., `/announcements`) without maintaining social presence
- **THEN** the user may remain reachable for chat if layout-level WS is active, but map sprites are not rendered

### Requirement: WebSocket presence on world tab

The system SHALL publish map spawn/update/despawn events only for users with presence context `world` in the same `sceneId`.

#### Scenario: User enters world scene

- **WHEN** a user opens `/world` in scene `hub-plaza`
- **THEN** eligible clients in `hub-plaza` receive spawn events for that user

#### Scenario: User leaves world tab

- **WHEN** a user navigates away from `/world` to `/home`
- **THEN** world scene clients receive despawn and home subscribers see at-home presence

### Requirement: Filtered presence broadcast

The server SHALL broadcast spawn/update events only to connections for whom `canSee(recipient, subject)` is true, except the Creator who receives all online adventurers across home and world contexts.

#### Scenario: Strangers do not see each other on map

- **WHEN** two users in different parties are both on `/world` in the same scene
- **THEN** neither client's map renders the other's sprite

### Requirement: Creator omniscience panel

The system SHALL provide the Creator a global online adventurer list showing all connected adventurers regardless of party, with presence labels (`home` or `world:{sceneId}`). Each entry SHALL offer locate (world only) and chat actions.

#### Scenario: Creator sees adventurer at home

- **WHEN** an adventurer is online on `/home`
- **THEN** the Creator's list shows that adventurer as at home with chat available

#### Scenario: Creator locates adventurer in world

- **WHEN** the Creator clicks locate on an adventurer in a world scene
- **THEN** if the Creator is on `/world`, the map switches to that scene and focuses the camera on the adventurer

#### Scenario: Creator initiates chat from omniscience list

- **WHEN** the Creator clicks chat on any online adventurer
- **THEN** a chat dialog opens with that adventurer

### Requirement: Heartbeat and stale cleanup

The system SHALL remove presence for connections that fail heartbeat within a configured timeout.

#### Scenario: Connection drop

- **WHEN** a client disconnects without graceful close
- **THEN** their sprite is removed within the heartbeat timeout
