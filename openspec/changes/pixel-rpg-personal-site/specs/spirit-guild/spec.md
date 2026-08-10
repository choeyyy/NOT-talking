## Status

**DISCUSSION** — 需求来自 2026-08-10 讨论；细节见 `discussion-log.md` §B。拍板前 **不纳入 V1 实现门禁**。

## ADDED Requirements

### Requirement: Spirit guild on workshop page

The system SHALL expose a **Spirit Guild** (精灵协会) section on `/workshop` for authorized participants. The guild SHALL consist of exactly **three** persona agents (spirits) with distinct seeded `agent_bindings`.

#### Scenario: Creator opens spirit guild

- **WHEN** the Creator navigates to the Spirit Guild area on `/workshop`
- **THEN** the UI shows the guild group chat and a list of dungeon script drafts with status

#### Scenario: Adventurers cannot access guild

- **WHEN** a non-Creator adventurer attempts to open the Spirit Guild API or UI
- **THEN** the server returns 403

### Requirement: Three spirits with fixed roles

The guild SHALL seed exactly three spirit agents with distinct roles and system prompts:

| Role id | Name (zh) | Responsibility |
|---------|-----------|----------------|
| `spirit_plot` | 剧情精灵 | Design narrative: node text, branches, choices, ending arcs |
| `spirit_engine` | 工程精灵 | Convert plot into schema-valid dungeon script JSON; tune numerical fields; output **DB drafts only** — MUST NOT modify repo code or require restart |
| `spirit_archivist` | 档案精灵 | Manage published scripts; analyze player run telemetry; recommend revisions |

#### Scenario: Plot spirit drafts narrative

- **WHEN** the guild starts a new dungeon draft
- **THEN** `spirit_plot` produces narrative structure and copy for nodes and endings before or in parallel with engineering

#### Scenario: Engine spirit produces deployable script

- **WHEN** plot content is ready for integration
- **THEN** `spirit_engine` outputs or updates a `dungeon_script_drafts` record with schema-valid JSON and tuned numeric fields

#### Scenario: Archivist reviews published dungeon

- **WHEN** the Creator or archivist requests analysis for a published dungeon id
- **THEN** `spirit_archivist` reads persisted logs and summarizes balance and completion issues in the guild thread or a linked report

### Requirement: Guild group chat participants

The Spirit Guild SHALL maintain a group conversation thread whose participants are: the Creator, the Creator's Son, and the three spirit agents. Messages SHALL be persisted for Creator audit (same policy as admin chat logs).

#### Scenario: Post in guild chat

- **WHEN** the Creator or Son sends a message in the guild thread
- **THEN** all spirit agents may be invoked according to routing rules and replies appear in the same thread

#### Scenario: Spirit proposes draft in chat

- **WHEN** a spirit agent produces a dungeon script draft
- **THEN** the draft is stored server-side and linked in the guild thread with status `drafting` or `pending_approval`

### Requirement: Spirits author dungeon scripts

The three spirit agents SHALL collaborate in role order (plot → engine → optional archivist feedback on revisions). Draft content SHALL conform to the dungeon script schema used by `dungeons` before publish. The engine spirit SHALL NOT publish directly; publication remains Creator-approved only.

#### Scenario: New draft created

- **WHEN** spirits finish a script draft for a new dungeon
- **THEN** a `dungeon_script_drafts` record is created with metadata (title, summary, target dungeon id or new id) and JSON script body

#### Scenario: Invalid draft blocked at publish

- **WHEN** a draft fails schema validation at publish time
- **THEN** publish is rejected and the guild thread receives an error summary; `dungeon_scripts`, entrances, and announcements are not updated

### Requirement: Runtime publish without application restart

Spirit Guild publication SHALL use the runtime dungeon catalog defined in `dungeons` (`dungeon_scripts`, optional `dungeon_entrances`). The engine spirit and publish pipeline MUST NOT depend on code deploy or process restart for new or updated scripts to become playable.

#### Scenario: Publish while agents keep running

- **WHEN** the Creator approves a draft while spirit agents are active in guild chat
- **THEN** the dungeon becomes enterable for new runs immediately after publish completes and agents remain available without restart

#### Scenario: Engine spirit never writes source files

- **WHEN** `spirit_engine` integrates a script
- **THEN** it updates `dungeon_script_drafts` via server API only; it does not create or patch `.ts` manifests or filesystem paths under the application repo

### Requirement: Offline drafting with Son facilitation

When the Creator is offline, spirit agents SHALL MAY continue drafting and revising scripts. The Creator's Son SHALL participate in guild chat but SHALL NOT publish drafts without Creator approval.

#### Scenario: Son continues thread while Creator offline

- **WHEN** the Creator is not present and spirits produce draft revisions
- **THEN** the Son may comment, summarize, and mark a draft `pending_approval` for the Creator's return

#### Scenario: Son cannot publish alone

- **WHEN** the Son attempts to approve or publish a draft without Creator consent recorded in the guild thread
- **THEN** the server rejects publish with 403

### Requirement: Creator approval via conversation

Publication SHALL require explicit Creator consent captured in the guild conversation (natural-language agreement and/or a structured confirm action). Upon approval, the system SHALL atomically: validate and upsert the runtime dungeon catalog (`dungeon_scripts`, optional `dungeon_entrances`), invalidate script loader cache, and create or update a world announcement — **without** application restart.

#### Scenario: Creator approves in chat

- **WHEN** the Creator expresses approval for a specific pending draft in the guild thread (per configured approval parser or explicit confirm command)
- **THEN** the draft status becomes `published`, the dungeon becomes playable, and a world announcement is upserted for all logged-in adventurers

#### Scenario: Announcement reflects new dungeon

- **WHEN** a draft is published successfully
- **THEN** the announcements list includes an entry describing the new or updated dungeon (title and summary at minimum)

#### Scenario: Creator rejects draft

- **WHEN** the Creator declines a pending draft in guild chat
- **THEN** the draft remains unpublished and status becomes `rejected` or returns to `drafting` per configuration

### Requirement: Published drafts are adventurer-facing only after release

Adventurers SHALL NOT see unpublished drafts. They SHALL discover released dungeons through existing `/world` dungeon entrances and the announcements tab after Creator approval.

#### Scenario: Draft invisible to adventurers

- **WHEN** a draft is in `drafting` or `pending_approval`
- **THEN** adventurers cannot select that dungeon from world entrances and no related announcement is shown

#### Scenario: Published dungeon playable

- **WHEN** a draft is published
- **THEN** adventurers with dungeon page access can enter the new dungeon from configured world entrances

### Requirement: Telemetry and dialogue logs for archivist

The system SHALL persist three log streams for Creator audit and archivist analysis. Adventurers MUST NOT read these logs via API or UI.

**`dungeon_ui_log`** — JRPG log/chat-box lines shown during a dungeon run (narrative text, choice labels, roll outcome summaries).

**`spirit_guild_log`** — all messages in the Spirit Guild group thread (Creator, Son, and three spirits).

**`dungeon_run_log`** — structured per-run events: `node_id`, d100 rolls and tiers, hp and gold deltas (wallet and run_gold), attribute changes, flags, exit settlement (ending tier, merged gold, soul potion drop result).

#### Scenario: UI log on each dungeon step

- **WHEN** the dungeon UI displays narrative or roll outcome text to the player
- **THEN** the same line is appended to `dungeon_ui_log` for that run id

#### Scenario: Run log on dice check

- **WHEN** the server resolves a d100 check during a dungeon run
- **THEN** a `dungeon_run_log` entry records roll value, tier, node id, and any hp/gold/attr deltas applied

#### Scenario: Run log on exit settlement

- **WHEN** a dungeon run completes with an ending resolution
- **THEN** `dungeon_run_log` records ending tier, final run_gold merge, dungeon_exp, and loot flags including soul potion drop if applicable

#### Scenario: Archivist queries run aggregates

- **WHEN** `spirit_archivist` is invoked to analyze a published dungeon
- **THEN** the server supplies aggregated metrics from `dungeon_run_log` and optional samples from `dungeon_ui_log` without exposing logs to adventurers

#### Scenario: Guild messages persisted

- **WHEN** any participant posts in the Spirit Guild thread
- **THEN** the message is stored in `spirit_guild_log` with sender, timestamp, and body

### Requirement: Archivist-driven script maintenance

The archivist spirit SHALL support reviewing published dungeon catalog entries, comparing telemetry against design intent, and proposing hotfix drafts (returned to plot/engine spirits). Hotfixes SHALL follow the same Creator approval flow as new scripts.

#### Scenario: Archivist flags overtuned node

- **WHEN** telemetry shows excessive hp loss or gold drain at a specific node across multiple runs
- **THEN** the archivist posts a summary in the guild thread referencing node id and suggested numeric adjustments for the engine spirit

#### Scenario: Hotfix draft for published dungeon

- **WHEN** spirits produce a revision draft for an already published dungeon
- **THEN** the draft references the source dungeon id and version; publish replaces or versions the live script only after Creator approval; adventurers with in-progress runs on that dungeon remain on their pinned version until exit

#### Scenario: Hotfix does not affect active players

- **WHEN** a hotfix is published while one or more adventurers are mid-run on that dungeon
- **THEN** those runs complete on the script version they started with; the hotfix applies only to runs that begin after publish completes
