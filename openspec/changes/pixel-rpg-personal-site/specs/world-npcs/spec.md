## ADDED Requirements

### Requirement: NPCs in world scenes

The system SHALL place non-player characters (NPCs) in registered world scenes via `world-npc-manifest` or Tiled object layers. Each NPC SHALL have a stable id, display name, sprite, and home scene.

#### Scenario: NPC visible in scene

- **WHEN** an adventurer enters a world scene containing registered NPCs
- **THEN** NPC sprites are rendered at configured positions

#### Scenario: Interact with static NPC

- **WHEN** an adventurer interacts with a static NPC in `/world`
- **THEN** a JRPG-style dialogue UI shows configured lines only

### Requirement: Static NPC dialogue only

All generic world NPCs SHALL use `mode: static` with predefined dialogue. They MUST NOT call the Cursor API.

#### Scenario: Static NPC speaks fixed lines

- **WHEN** an adventurer talks to a static NPC
- **THEN** configured dialogue lines are shown in order or from a defined tree

#### Scenario: Static NPC ends conversation

- **WHEN** the adventurer closes the dialogue or reaches the end of static lines
- **THEN** the dialogue UI closes with no AI request made

### Requirement: Creator's Son world interactable

The Creator's Son SHALL have a dedicated interactable or sprite in a world scene (e.g., hub-plaza) that opens the Son chat dialog. The Son is the only persona agent; generic NPCs remain static.

#### Scenario: Interact with Son in world

- **WHEN** an adventurer interacts with the Creator's Son in `/world`
- **THEN** the Son chat dialog opens for AI conversation and optional gold grants

### Requirement: NPC registry via manifest

NPC definitions SHALL be configured via manifest by the Creator deploy process. Adventurers MUST NOT edit NPC definitions.

#### Scenario: Creator adds static NPC via manifest

- **WHEN** a new static NPC entry is added to the manifest
- **THEN** the NPC appears in the configured world scene
