## Status

**DISCUSSION** — 2026-08-11 用户提案；嵌入 `/admin/studio`；见 `discussion-log.md` §K。

> **实现状态：** propose 阶段，**无代码原型**；apply 时再设计 UI 与 MCP 接入。

## ADDED Requirements

### Requirement: MCP-connected collaborative drawing

The pixel studio SHALL expose an **MCP server** (path TBD at implementation) backed by a **local bridge** (HTTP + WebSocket) so Cursor AI can:

- Draw pixels, fill rects, paint scene tiles, and place objects via `studio_*` tools
- Read snapshots and full state after the Creator adjusts drawings in the browser UI

The browser studio and MCP SHALL share **one live state**: AI edits appear in the UI; Creator manual edits sync back for AI to read via `studio_get_snapshot` / `studio_get_state`.

#### Scenario: AI draws item sprite, Creator adjusts

- **WHEN** AI calls `studio_draw_pixels` on the item tab and the Creator then edits pixels in `/admin/studio`
- **THEN** the bridge revision increments; AI's next `studio_get_snapshot` reflects the Creator's changes

#### Scenario: Bridge offline

- **WHEN** the bridge server is not running
- **THEN** the browser studio works standalone; MCP tools fail with connection error until `npm run server` is started

### Requirement: AI recognizes studio exports

When the Creator submits a drawing from **像素工坊** (`/admin/studio`) — character layer, item sprite, tile, or scene fragment — the system SHALL offer **AI recognition** via the server-side Cursor API (vision-capable model when image input is supported). Recognition SHALL NOT run in the browser with API keys exposed.

The recognition result SHALL include at minimum:

| Field | Meaning |
|-------|---------|
| `kind` | `tile` \| `item` \| `character_part` \| `npc_sprite` \| `ui` \| `unknown` |
| `label` | Short Chinese/English description for admin UI |
| `suggestedObjectType` | For scene placement: e.g. `npc`, `tavern_table`, `prop`, `dungeon_entrance` (optional) |
| `tags` | Style/theme tags for search |
| `confidence` | `high` \| `medium` \| `low` |

Structured studio export metadata (grid size, layer id, existing `objectType` if drawn in scene mode) SHALL be sent alongside the image so AI can combine **pixels + context**, not vision alone.

#### Scenario: Creator requests recognition after drawing item

- **WHEN** the Creator clicks **识别并放置** on a 32×32 item export in `/admin/studio`
- **THEN** the server returns recognition JSON and shows a placement panel; the asset PNG is stored as a pending **`studio_asset`** draft until placed or discarded

#### Scenario: Recognition fails

- **WHEN** the AI call fails or returns `unknown` with low confidence
- **THEN** the Creator may still manually choose target scene, coordinates, and object type before placement

### Requirement: Creator specifies placement target

After recognition (or manual skip), the Creator SHALL specify where the asset belongs using **one or more** of:

1. **Explicit grid** — `sceneId`, `x`, `y` (tile coordinates)
2. **Interactable binding** — `objectType` + properties (e.g. `tavern_table` + `tableId`, `npc` + `dialogueId`)
3. **Natural language hint** — e.g. `tavern-hall` bar left; server MAY use AI to propose coordinates on that scene, **requiring Creator confirm** before write

The system MUST NOT auto-publish to live `/world` without an explicit **确认放置** or **发布场景** action by the Creator.

#### Scenario: Explicit coordinates

- **WHEN** the Creator selects scene `tavern-hall`, tile (8, 5), and object type `tavern_menu`
- **THEN** the pending asset is written into that scene's object list (or staging draft) at the given tile

#### Scenario: Natural language placement proposal

- **WHEN** the Creator enters 「放到 hub-plaza 公告板旁边」 with a pending prop sprite
- **THEN** the server returns a **proposed** `{ sceneId, x, y, objectType }` with rationale; live map unchanged until Creator confirms

### Requirement: Placement writes staging then publish

Recognized and placed assets SHALL follow a **staging → publish** pipeline:

| Stage | Store | Visible to adventurers |
|-------|-------|------------------------|
| **Draft** | `studio_assets` + `scene_drafts` (or studio JSON patch) | No |
| **Published** | `public/assets/` + runtime scene manifest / `dungeon_entrances` / NPC manifest as applicable | Yes on next load |

Placement SHALL update **staging** first. **`POST /api/admin/scenes/publish`** (or equivalent) promotes staging to live assets and invalidates world loader cache per `dungeons` / world-map runtime rules.

#### Scenario: Place without publish

- **WHEN** the Creator confirms placement but does not publish
- **THEN** adventurers on `/world` still see the previous scene until publish

#### Scenario: Publish after placement

- **WHEN** the Creator publishes the scene draft
- **THEN** new tileset/object PNGs are copied to assets volume, scene manifest updates, and `/world` loads the new layout without application restart

### Requirement: Recognition and placement audit

Each recognize and place action SHALL log to **`player_behavior_log`** or a dedicated **`admin_audit_log`** with: Creator id, asset id, recognition summary, target scene/coords, AI vs manual, timestamp. Creator-only read.

#### Scenario: Audit trail for AI placement

- **WHEN** the Creator completes a confirmed AI-assisted placement
- **THEN** an audit entry records before/after scene object snapshot reference

### Requirement: Adventurers cannot trigger studio AI placement

Only users with `is_admin=true` MAY call recognize/place/publish studio APIs.

#### Scenario: Adventurer forbidden

- **WHEN** a non-admin calls `POST /api/admin/studio/place`
- **THEN** the server returns 403
