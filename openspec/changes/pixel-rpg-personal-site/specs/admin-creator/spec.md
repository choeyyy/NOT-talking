## ADDED Requirements

### Requirement: Creator admin hub

The system SHALL provide a unified **创世主后台** at `/admin/*` as the Creator's command center. Non-adventurer operational tools (scene authoring, global asset library, log audit, Son configuration, Gnome Guild publish pipeline, user/region CRUD) SHALL live under `/admin` rather than in adventurer-facing tabs.

The Creator SHALL also reach **all adventurer-facing routes** (`/home`, `/workshop`, `/world`, `/dungeon`, `/gallery`, `/profile`, etc.) from admin navigation or omniscience links for preview and support, bypassing region restrictions where appropriate.

When the Creator logs in, the **primary world and player-visible pages** SHALL be available immediately (same routes adventurers use). Opening guild agent chats (Gnome Guild, Tall Folk) MUST NOT happen automatically on login; those agents wake only when the Creator opens the respective chat panel per `gnome-guild` and `tall-folk-guild`.

#### Scenario: Creator opens admin hub

- **WHEN** a user with `is_admin=true` navigates to `/admin`
- **THEN** a dashboard or sidebar lists admin modules and shortcuts to player pages

#### Scenario: Creator previews player page from admin

- **WHEN** the Creator clicks a preview link for `/world` or `/home` from admin
- **THEN** the corresponding player route opens in the same session without requiring a separate login

#### Scenario: Creator sees main world on login without waking guild agents

- **WHEN** the Creator logs in and navigates to `/world`
- **THEN** the world loads like for adventurers and no Gnome or Tall Folk Cursor API calls occur until the Creator opens a guild chat panel

#### Scenario: Non-admin blocked from admin

- **WHEN** an adventurer requests `/admin` or any `/admin/*` route
- **THEN** the system returns 403 or redirects with access denied

### Requirement: Admin navigation modules

The Creator admin area SHALL include at minimum these modules (routes may be grouped in one layout):

| Module | Route (example) | Purpose |
|--------|-----------------|--------|
| **Dashboard / 神视** | `/admin` | Online list, locate, quick chat |
| **冒险者名册** | `/admin/users` | User CRUD, party, acquaintance override |
| **区域权限** | `/admin/regions` | Page access matrix |
| **世界公告** | `/admin/announcements` | Announcement CRUD |
| **像素工坊** | `/admin/studio` | Scene build + global asset library (embed `pixel-studio`) |
| **场景 / 入口** | `/admin/scenes` | Scene manifest, dungeon entrances, publish |
| **NPC** | `/admin/npcs` | Dialogue (对玩家说的话), **player address** (对玩家的称呼), sprite, placement — T0 hot update |
| **聊天 Log** | `/admin/chat-logs` | DM history audit |
| **行为 Log** | `/admin/behavior-logs` | `player_behavior_log`, dungeon telemetry summary |
| **之子** | `/admin/son` | `son_wallet_gold`, grant audit, Son agent settings |
| **地精协会** | `/admin/gnome-guild` | Guild chat, drafts, publish; Creator may **hand-edit** drafts |
| **副本剧本** | **`/admin/dungeons`** | Edit drafts + published scripts (`dungeon_scripts`); **T0 hotfix** publish |
| **长身人修会** | `/admin/tall-folk` | Runtime patches (T0), deploy queue (T2), diagnostics from logs |
| **Agent 安全** | `/admin/agents` | Kill switch, rate limit config, circuit breaker status, audit tail |
| **赋活 / Life** | `/admin/life` | V2+ NPC/object grants |
| **玩家页面** | links | Open `/home`, `/world`, `/workshop`, … as Creator preview |

#### Scenario: Creator opens pixel studio in admin

- **WHEN** the Creator opens `/admin/studio`
- **THEN** the embedded pixel studio provides **scene搭建**, asset drawing, **AI recognize-and-place** per `admin-studio`, and export to staging

#### Scenario: Creator confirms AI placement

- **WHEN** the Creator confirms a proposed placement for a recognized asset
- **THEN** the scene draft updates in staging and audit log records the action; live `/world` unchanged until scene publish

#### Scenario: Adventurer does not get admin studio

- **WHEN** a non-admin adventurer navigates to `/admin/studio`
- **THEN** access is denied

### Requirement: Adventurer-facing editors vs admin studio

Adventurers SHALL customize **their own** character and creations on player routes without admin access:

| Capability | Adventurer route | Creator admin |
|------------|------------------|---------------|
| 捏人 / 角色 sprite | `/profile` (character editor) | Preview only; optional template parts published from `/admin/studio` |
| 造物 sprite | `/workshop` (item editor) | Preview + audit creations list in admin |
| **场景 / 大世界地图** | Play only on `/world` | **Author only** in `/admin/studio` |

#### Scenario: Creator builds tavern scene in admin

- **WHEN** the Creator exports a scene from `/admin/studio` and publishes via `/admin/scenes`
- **THEN** adventurers see the updated map on `/world` without access to the editor

### Requirement: Creator admin area access

The system SHALL restrict `/admin/*` routes to users with `is_admin=true`.

#### Scenario: Non-admin accesses admin

- **WHEN** a non-admin user requests `/admin/users`
- **THEN** the system returns 403 or redirects with an access denied message

### Requirement: User CRUD by Creator

The system SHALL allow the Creator to create, list, update (including disable/enable), and delete adventurer accounts.

#### Scenario: Creator disables adventurer

- **WHEN** the Creator disables a user account
- **THEN** that user cannot log in or maintain an active session

### Requirement: Region access matrix CRUD

The system SHALL allow the Creator to grant or revoke page/region access per user via a matrix or equivalent UI bound to registered pages.

#### Scenario: Creator grants region access

- **WHEN** the Creator grants a user access to a registered page
- **THEN** that user can navigate to the corresponding route and API

### Requirement: Party assignment for social isolation

The system SHALL allow the Creator to create parties (groups) and assign each adventurer to one party. Users in different parties SHALL be treated as strangers per `social-visibility` **unless** they share a mutual `user_acquaintances` link.

The Creator MAY also create or remove **direct acquaintance links** between adventurers without tavern ritual (admin override).

#### Scenario: Creator assigns party

- **WHEN** the Creator moves a user from Party A to Party B
- **THEN** the user no longer sees members of Party A on map, chat, or gallery (except Creator omniscience and any separate `user_acquaintances` links)

### Requirement: Creator funds Son agent wallet

The Creator SHALL manage a dedicated `son_wallet_gold` balance used only for Creator's Son chat gold grants to adventurers.

#### Scenario: Creator tops up Son wallet

- **WHEN** the Creator adds gold to the Son wallet in admin
- **THEN** `son_wallet_gold` increases immediately

#### Scenario: View Son wallet balance

- **WHEN** the Creator opens Son agent settings in admin
- **THEN** current `son_wallet_gold` and recent grant audit entries are shown

### Requirement: Creator narrative labels

The admin UI SHALL use Creator/adventurer/region/world narrative copy consistent with the pixel TRPG theme.

#### Scenario: Admin UI display

- **WHEN** the Creator views the user management page
- **THEN** labels reflect TRPG terminology (e.g., adventurer roster, region permissions)

### Requirement: Creator behavior and dungeon log audit

The system SHALL provide admin pages for **`player_behavior_log`** and summarized **`dungeon_run_log`** / **`dungeon_ui_log`** / **`gnome_guild_log`** (as implemented), readable only by the Creator.

#### Scenario: Creator audits behavior log

- **WHEN** the Creator opens `/admin/behavior-logs` and filters by adventurer or event type
- **THEN** persisted behavior log entries are listed chronologically

### Requirement: Creator chat log audit

The system SHALL provide the Creator an admin interface to browse persisted direct-message logs between adventurers and between Creator and adventurers.

#### Scenario: Creator audits conversation

- **WHEN** the Creator opens the chat log audit page and selects a conversation
- **THEN** the full message history for that thread is displayed
