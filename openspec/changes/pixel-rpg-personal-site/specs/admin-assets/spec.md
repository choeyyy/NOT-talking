## Status

**DISCUSSION** — 2026-08-11 用户提案；`/admin/assets`；见 `discussion-log.md` §P。

## ADDED Requirements

### Requirement: Unified art asset registry

The system SHALL maintain a **unified art asset registry** (DB e.g. `art_assets`) for all PNG/sprite/tileset resources used by `/world`, NPCs, dungeons, and player customization.

Each row SHALL include at minimum:

| Field | Meaning |
|-------|---------|
| `id` | Stable internal id |
| `asset_number` | Creator-assigned **catalog number** (标号) for lookup; unique when set |
| `scope` | `global` \| `player` |
| `owner_user_id` | NULL for global; adventurer id for player-owned assets |
| `kind` | e.g. `tile`, `tileset`, `npc_sprite`, `prop`, `character_sprite`, `creation_sprite`, `ui`, `other` |
| `storage_url` | File path or blob URL under uploads volume |
| `width`, `height` | Pixel dimensions |
| `label`, `tags`, `notes` | Creator-editable **details** (online, no redeploy) |
| `source` | e.g. `admin_studio`, `profile`, `workshop`, `import`, `seed` |
| `version` | Incremented on file replace or metadata publish |

Bootstrap seed assets MAY populate initial rows; runtime authoring adds more via studio, players, or admin import.

#### Scenario: Global and player assets in one catalog

- **WHEN** the Creator opens `/admin/assets`
- **THEN** the list includes global world art and player-uploaded character/creation sprites with filters by scope, kind, and owner

### Requirement: Creator admin asset management

The Creator SHALL manage **existing** art assets at **`/admin/assets`** without redeploy:

- Assign or change **`asset_number`** (标号)
- Edit **label, tags, notes**, and kind classification
- Replace PNG (optional upload) with version bump
- Link asset to consumers where applicable (NPC sprite id, creation id, manifest ref)

Changes to **metadata** SHALL be **T0 hot update** (DB + cache invalidate). Replacing image bytes SHALL invalidate dependent loaders (NPC, world, character preview) on next fetch.

Adventurers MUST NOT access `/admin/assets` or reassign global catalog numbers.

#### Scenario: Creator labels asset online

- **WHEN** the Creator sets `asset_number` `T-042` and tag `tavern-hall` on a tile PNG
- **THEN** the row updates immediately and appears in admin search by number or tag

#### Scenario: Creator edits player creation sprite metadata

- **WHEN** the Creator adds audit notes to a player-owned `creation_sprite` asset
- **THEN** the notes save without changing player ownership of the creation; the asset remains in the player scope catalog

#### Scenario: Creator replaces global NPC sprite file

- **WHEN** the Creator uploads a new PNG for an `npc_sprite` asset linked to `li_luang`
- **THEN** `art_assets.version` increments, cache invalidates, and `/world` loads the new sprite on next scene/NPC refresh per `world-npcs` hot-update rules

### Requirement: Player assets stored in registry

When an adventurer saves **character** (`/profile`) or **creation** (`/workshop`) sprites, the server SHALL register or update a corresponding **`scope: player`** row in `art_assets` (linked to `users.character_config` or `creations.id`). Player files SHALL remain stored on the server volume; the Creator MAY view and annotate them in `/admin/assets` but MUST NOT delete player-owned assets without explicit admin moderation action (TBD policy: soft-hide vs hard delete).

#### Scenario: Player saves workshop item

- **WHEN** an adventurer uploads a creation sprite in `/workshop`
- **THEN** a player-scoped `art_assets` row is created with `source: workshop` and linked `owner_user_id`

#### Scenario: Player character avatar update

- **WHEN** an adventurer saves a new character composite from `/profile`
- **THEN** the registry records a new or updated `character_sprite` asset for that user

### Requirement: Asset picker integration

Admin modules that reference sprites ( **`/admin/npcs`**, **`/admin/scenes`**, **`/admin/studio`**) SHALL allow selecting assets by **id** or **asset_number** from the registry rather than raw path strings only.

#### Scenario: NPC sprite picked from catalog

- **WHEN** the Creator assigns a sprite to `li_luang` in `/admin/npcs`
- **THEN** the NPC record stores `art_asset_id` referencing the registry row

### Requirement: Audit trail for asset changes

Creator edits to asset metadata or file replacement SHALL log to admin audit (who, asset id, before/after summary, timestamp).

#### Scenario: Asset relabel audited

- **WHEN** the Creator changes `asset_number` on a global tile
- **THEN** an audit entry records the old and new catalog number
