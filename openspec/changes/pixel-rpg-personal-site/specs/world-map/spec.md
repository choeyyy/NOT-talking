## ADDED Requirements

### Requirement: World tab for sightseeing and social play

The system SHALL provide a `/world` tab as an expandable big-world space whose primary purpose is sightseeing and social interaction (chat, meeting acquaintances). Functional app pages SHALL be reached via portal doors, not by replacing the entire site with the game canvas.

#### Scenario: User opens world tab

- **WHEN** an authenticated user navigates to `/world`
- **THEN** a Phaser canvas loads with collision and the user's character sprite in the default world scene

### Requirement: Multi-scene world with scene manifest

The big world SHALL support multiple Phaser scenes registered in a code manifest (`world-scene-manifest`). New scenes SHALL be addable by registering a Tiled map and door links without changing core protocols.

#### Scenario: Scene transition via door

- **WHEN** a user interacts with a `scene_door` object pointing to a registered target scene
- **THEN** the client transitions to that scene with a fade and spawns at the configured spawn point

#### Scenario: Add new scene in future release

- **WHEN** a new scene is added to the manifest and Tiled assets are deployed
- **THEN** existing scenes can link to it via new door objects without schema migration

### Requirement: World interactable types

World interactables SHALL support `scene_door`, `portal_door`, and `dungeon_entrance` objects, plus NPC interactable references per `world-npc-manifest`.

#### Scenario: Portal to functional page

- **WHEN** a user interacts with a permitted `portal_door` to `/gallery`
- **THEN** world presence is left and the app navigates to `/gallery`

#### Scenario: Locked portal

- **WHEN** a user interacts with a `portal_door` for a page they lack access to
- **THEN** a JRPG-themed denial dialog is shown

#### Scenario: Dungeon entrance from world

- **WHEN** a user interacts with a permitted `dungeon_entrance` linked to dungeon id `sample-cave`
- **THEN** world presence is left and the app navigates to `/dungeon/sample-cave`

#### Scenario: Runtime DB entrance merged with map

- **WHEN** an active row exists in `dungeon_entrances` for the current scene
- **THEN** the world client shows that entrance alongside Tiled `dungeon_entrance` objects without redeploying map assets

### Requirement: Keyboard movement with collision

The system SHALL support keyboard movement (WASD or arrow keys) with tile/building collision on each world scene.

#### Scenario: User walks into wall

- **WHEN** the user moves toward a collision tile
- **THEN** the character does not pass through

### Requirement: Per-scene presence rooms

Online map presence SHALL be scoped to `room:world:{sceneId}`. Adventurers SHALL only receive spawn/update events for acquaintances in the same world scene.

#### Scenario: Users in different scenes

- **WHEN** two acquaintances are online on `/world` but in different scenes
- **THEN** neither sees the other's sprite until they enter the same scene

### Requirement: Initial world scene pack

The first release SHALL ship at least these manifest scenes: `hub-plaza` (default spawn), `garden-view`, `tavern-hall`, `shrine-outer`, and `portrait-hall`, with at least one `portal_door` to `/gallery` and at least one `dungeon_entrance` to a registered dungeon.

#### Scenario: Default spawn

- **WHEN** a user enters `/world` for the first time in a session
- **THEN** they spawn in `hub-plaza`

### Requirement: Phaser bundle isolation

Phaser and world map assets SHALL be dynamically imported only for `/world` and `/dungeon` tabs to avoid loading game code on unrelated tabs.

#### Scenario: User on home tab without world Phaser

- **WHEN** a user is on `/home` in V1
- **THEN** world Phaser map code is not required to load

### Requirement: Portrait hall portal

The world SHALL include a path to the gallery via `portrait-hall` scene and/or a `portal_door` to `/gallery`.

#### Scenario: Walk to gallery portal

- **WHEN** a user interacts with the gallery portal from the world
- **THEN** the user is navigated to `/gallery` if permitted
