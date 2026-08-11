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

### Requirement: NPC registry and Creator admin edit

Static NPC definitions SHALL be loaded from a **runtime registry** (DB table e.g. `world_npcs`, synced from seed manifest on bootstrap). The Creator SHALL edit **all** static NPCs via **`/admin/npcs`**, including at minimum:

| Field | Meaning |
|-------|---------|
| **Dialogue** | What the NPC **says to players** — static lines / dialogue tree (语录) |
| **Player address** | How the NPC **calls players** — e.g. Li-Luang uses **乖孙** |
| **Display name, sprite, scene placement** | As before |

Both **dialogue** and **player address** are **Creator-maintained** in admin (no spec example copy). Runtime dialogue UI SHALL apply the configured **player address** when rendering lines (substitution or template slot per implementation).

**Hot update (T0):** Saving in admin SHALL upsert DB and **invalidate** the server NPC loader cache **without** application restart or redeploy. This is the same tier as gnome dungeon script publish (see `tall-folk-guild` T0).

**Frontend freshness:**

| Trigger | Behavior |
|---------|----------|
| **Next load** | Entering a world scene or calling `GET /api/world/npcs?sceneId=` after invalidate returns latest NPCs |
| **Next interact** | Talking to an NPC always fetches current lines from server (not stale client-only cache) |
| **Live in scene (recommended)** | After admin save, server MAY broadcast `world_npcs_updated` on WS for that `sceneId`; clients in `/world` on that scene reload NPC sprites/lines **without full page refresh** |

Adventurers MUST NOT edit NPC definitions.

The Son agent binding is edited separately under `/admin/son`; this requirement covers **static** NPCs only.

#### Scenario: Creator edits Li-Luang dialogue

- **WHEN** the Creator saves updated `li_luang` lines in `/admin/npcs`
- **THEN** the DB row updates, cache is invalidated, and the next interaction in `tavern-hall` shows the new lines

#### Scenario: Adventurer already in tavern when Creator saves

- **WHEN** the Creator saves an NPC change for `tavern-hall` and WS broadcast is enabled
- **THEN** adventurers currently in `tavern-hall` receive updated NPC presentation without restarting the app; if WS is not implemented yet, updates appear on next scene re-enter or next NPC talk

#### Scenario: Creator previews change immediately

- **WHEN** the Creator saves from `/admin/npcs` and opens `/world` in the same scene
- **THEN** the Creator sees the updated NPC without redeploy

#### Scenario: Creator adds static NPC

- **WHEN** the Creator creates a new static NPC row in admin
- **THEN** the NPC appears in the configured world scene after cache invalidate

#### Scenario: Adventurer cannot edit NPCs

- **WHEN** a non-admin calls NPC admin APIs
- **THEN** the server returns 403

### Requirement: Tavern bartender Li-Luang (seed)

Bootstrap SHALL seed **`li_luang`** in `tavern-hall`: **`Li-Luang`**, grandmother. Seed **characterization** (Creator fills concrete text in admin): dialogue theme **drinks are AA**; **player address 乖孙**.

#### Scenario: Li-Luang present in tavern

- **WHEN** the world loads `tavern-hall`
- **THEN** `li_luang` is present at the bar with Creator-configured sprite and lines
