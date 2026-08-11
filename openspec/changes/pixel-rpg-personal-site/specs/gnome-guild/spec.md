## Status

**DISCUSSION** — 需求来自 2026-08-10 讨论；细节见 `discussion-log.md` §B。拍板前 **不纳入 V1 实现门禁**。

## ADDED Requirements

### Requirement: Spirit guild on workshop page

The system SHALL expose a **Gnome Guild** (地精协会) section on `/workshop` for authorized participants. The guild SHALL consist of exactly **three** persona agents (gnomes) with distinct seeded `agent_bindings`.

#### Scenario: Creator opens gnome guild

- **WHEN** the Creator navigates to the Gnome Guild area on `/workshop` or the world guild interactable
- **THEN** the UI shows the guild group chat and a list of dungeon script drafts with status

### Requirement: Spirit guild visible in big world

The big world (`/world`) SHALL display a **Gnome Guild council** (地精会议) interactable — visible sprite, door, or scene facade that all logged-in adventurers can see and walk to. This world presence is **flavor and world-building**; it is not hidden behind `canSee` party rules unless configured otherwise.

#### Scenario: Adventurer sees guild in world

- **WHEN** any logged-in adventurer enters a scene that contains the gnome guild interactable
- **THEN** the guild meeting UI facade (building, door glow, sign, or similar) is rendered like other world landmarks

#### Scenario: Adventurer walks to guild entrance

- **WHEN** an adventurer approaches the guild interactable on the map
- **THEN** an interact hint is shown (e.g., prompt to enter or knock)

### Requirement: Adventurers turned away at the door

Adventurers MUST NOT enter the functional Gnome Guild (chat, drafts, publish). When an adventurer attempts to enter via the world interactable or any non-Creator API, the system SHALL show a **JRPG-style refusal dialog**. The refusal MUST be **random each time**: the server randomly selects one of the three gnomes as speaker and returns a **short in-character refusal** (AI via that gnome's `agent_binding`, with strict length/token cap and refusal-only prompt). If AI is unavailable or rate-limited, the server SHALL fall back to a **random static line** from that gnome's pool in `gnome-guild-manifest`. The manifest SHALL include a **shared canonical refusal** used by all three gnomes:

> **「让我来看看是谁没被邀请。」**

This line MUST appear in every gnome's static refusal pool (or a shared `defaultRefusalLines` pool merged at runtime). AI-generated refusals SHOULD stay in the same tone (turn away uninvited visitors; no guild spoilers).

#### Scenario: Adventurer rejected at world entrance

- **WHEN** a non-Creator adventurer interacts with the world gnome guild entrance
- **THEN** a themed dialog shows a refusal spoken by a randomly chosen gnome; guild chat and draft UI do not open

#### Scenario: Canonical static refusal available

- **WHEN** static fallback is selected for a gnome refusal
- **THEN** the pool MAY return **「让我来看看是谁没被邀请。」** among other manifest lines

#### Scenario: Random gnome speaker each attempt

- **WHEN** an adventurer is rejected on two consecutive interactions
- **THEN** the speaker MAY differ between attempts (random among `gnome_plot`, `gnome_engine`, `gnome_archivist`)

#### Scenario: AI refusal with static fallback

- **WHEN** the server generates an AI refusal for the selected gnome and the Cursor API call fails
- **THEN** a random static refusal line for that gnome from manifest is shown instead

#### Scenario: AI refusal stays on-topic

- **WHEN** an AI refusal is generated
- **THEN** the prompt constrains output to a brief turn-away message with no guild spoilers, no publish hints, and no invitation to adventurers

#### Scenario: Rejection logged

- **WHEN** an adventurer receives a gnome refusal at the world entrance
- **THEN** `player_behavior_log` records `gnome_guild_rejection` with gnome id and whether the line was `ai` or `static`

#### Scenario: Adventurer guild API forbidden

- **WHEN** a non-Creator adventurer calls Gnome Guild chat, draft, or publish APIs
- **THEN** the server returns 403 with no guild data leakage

#### Scenario: Creator enters from world

- **WHEN** the Creator interacts with the world gnome guild entrance
- **THEN** the full Gnome Guild UI opens (same capabilities as `/workshop` guild panel)

### Requirement: Three gnomes with fixed roles

The guild SHALL seed exactly three gnome agents with distinct roles and system prompts:

| Role id | Name (zh) | Responsibility |
|---------|-----------|----------------|
| `gnome_plot` | 剧情地精 | Design narrative: node text, branches, choices, ending arcs |
| `gnome_engine` | 工程地精 | Convert plot into schema-valid dungeon script JSON; tune numerical fields; output **DB drafts only** — MUST NOT modify repo code or require restart |
| `gnome_archivist` | 档案地精 | Manage published scripts; analyze player run telemetry; recommend revisions |

#### Scenario: Plot gnome drafts narrative

- **WHEN** the guild starts a new dungeon draft
- **THEN** `gnome_plot` produces narrative structure and copy for nodes and endings before or in parallel with engineering

#### Scenario: Engine gnome produces deployable script

- **WHEN** plot content is ready for integration
- **THEN** `gnome_engine` outputs or updates a `dungeon_script_drafts` record with schema-valid JSON and tuned numeric fields

#### Scenario: Archivist reviews published dungeon

- **WHEN** the Creator or archivist requests analysis for a published dungeon id
- **THEN** `gnome_archivist` reads persisted logs and summarizes balance and completion issues in the guild thread or a linked report

### Requirement: Guild group chat participants

The Gnome Guild SHALL maintain a group conversation thread whose participants are: the Creator, the Creator's Son, and the three gnome agents. Messages SHALL be persisted for Creator audit (same policy as admin chat logs).

#### Scenario: Post in guild chat

- **WHEN** the Creator or Son sends a message in the guild thread
- **THEN** all gnome agents may be invoked according to routing rules and replies appear in the same thread

#### Scenario: Spirit proposes draft in chat

- **WHEN** a gnome agent produces a dungeon script draft
- **THEN** the draft is stored server-side and linked in the guild thread with status `drafting` or `pending_approval`

### Requirement: Spirits author dungeon scripts

The three gnome agents SHALL collaborate in role order (plot → engine → optional archivist feedback on revisions). Draft content SHALL conform to the dungeon script schema used by `dungeons` and **MUST** use the shared d100 tier rules in `trpg-mechanics` (`house-coc` profile). The engine gnome SHALL NOT publish directly; publication remains Creator-approved only.

### Requirement: Spirit agents synchronized with d100 rules

The server SHALL inject the canonical **`house-coc`** d100 resolver rules (tier keys, band conditions, fallback behavior) into **all three** gnome agent system prompts and into publish-time JSON schema validation. Plot, engine, and archivist gnomes MUST author and review scripts against the same rules as runtime gameplay.

**Plot gnome (`gnome_plot`):** When designing branches, label intended tiers in outline (e.g., hidden door on `hard_success`, catastrophe on `crit_failure`). MUST NOT specify alternate tier names. For dungeons with **`supportsParty: true`**, plot gnome MUST outline **`partyVariants`** for key nodes — how narrative, hazards, choices, and failure consequences **change when 2+ adventurers** face the same beat (not DC math alone).

**Engine gnome (`gnome_engine`):** When building check nodes, MUST output `outcomes` keyed only by canonical tiers; set `dc` and optional `stat`; tune SAN/hp/gold deltas per tier. MUST encode **`partyCheck`** and **`partyVariants`** from plot handoff into schema-valid JSON. MUST run schema + tier validation before marking draft `pending_approval`.

**Archivist gnome (`gnome_archivist`):** When analyzing telemetry, SHALL aggregate `dungeon_run_log` by resolved tier keys and flag scripts whose `crit_failure` or `failure` rates imply DC mis-tuning. SHALL compare **solo vs party** run metrics when `party_size` is present in logs and flag nodes where party variants may be missing or overtuned.

#### Scenario: Engine draft uses standard tiers

- **WHEN** `gnome_engine` produces a check node for a draft
- **THEN** outcomes include at least `success` and `failure`, and any crit branches use keys `crit_success` / `crit_failure` only

#### Scenario: Publish rejects non-canonical tier in gnome draft

- **WHEN** a gnome-produced draft contains outcome key `大成功` or `big_success`
- **THEN** publish validation fails with tier key error before the dungeon goes live

#### Scenario: Spirit prompt includes resolver summary

- **WHEN** any gnome agent binding is loaded for guild chat or drafting
- **THEN** its system prompt includes an embedded summary of `house-coc` rules matching `trpg-mechanics` spec

#### Scenario: Plot outline references tiers for engine handoff

- **WHEN** `gnome_plot` delivers a dungeon outline to `gnome_engine`
- **THEN** check nodes include intended tier labels mapped to canonical tier names; if `supportsParty`, per-node notes for `partyVariants` at `minPartySize` 2+ (text change, extra hazard, alternate branch)

#### Scenario: Engine encodes partyVariants from plot

- **WHEN** `gnome_engine` integrates a co-op dungeon draft
- **THEN** each plot-marked node includes valid `partyVariants[]` with `minPartySize`, optional `text`, `onEnter`, `outcomes`, `next`, and optional `partyCheck` overrides

#### Scenario: New draft created

- **WHEN** gnomes finish a script draft for a new dungeon
- **THEN** a `dungeon_script_drafts` record is created with metadata (title, summary, target dungeon id or new id) and JSON script body

#### Scenario: Invalid draft blocked at publish

- **WHEN** a draft fails schema validation at publish time
- **THEN** publish is rejected and the guild thread receives an error summary; `dungeon_scripts`, entrances, and announcements are not updated

### Requirement: Runtime publish without application restart

Gnome Guild publication SHALL use the runtime dungeon catalog defined in `dungeons` (`dungeon_scripts`, optional `dungeon_entrances`). The engine gnome and publish pipeline MUST NOT depend on code deploy or process restart for new or updated scripts to become playable.

**Separation from agent wake state:** Published scripts live in **DB**, not in gnome agent memory. The always-running game server loads scripts via `DungeonScriptLoader` on each **new dungeon run**. Gnomes need only be awake during the Creator's guild chat session to **author drafts**; once published, adventurers consume the DB catalog while gnomes are dormant again.

#### Scenario: Published script available while gnomes dormant

- **WHEN** a draft was published yesterday and the Creator has not opened the guild chat today
- **THEN** adventurers can still start that dungeon from `/world` because `dungeon_scripts` is read from DB by the always-running backend

#### Scenario: Publish updates live catalog without restart

- **WHEN** the Creator approves publish during an active guild session
- **THEN** the server upserts `dungeon_scripts`, invalidates the script loader cache, and new dungeon runs immediately load the new version; the main app and Son remain running throughout

#### Scenario: In-progress run unaffected by publish

- **WHEN** adventurers are mid-run on dungeon id `X` and a hotfix for `X` is published
- **THEN** those runs keep their pinned `script_version`; only new runs after publish load the updated script

#### Scenario: Publish while agents keep running

- **WHEN** the Creator approves a draft while gnome agents are active in guild chat
- **THEN** the dungeon becomes enterable for new runs immediately after publish completes and agents remain available without restart

#### Scenario: Engine gnome never writes source files

- **WHEN** `gnome_engine` integrates a script
- **THEN** it updates `dungeon_script_drafts` via server API only; it does not create or patch `.ts` manifests or filesystem paths under the application repo

### Requirement: Lazy wake on Creator chat open

Gnome agents SHALL remain **dormant** (no Cursor API calls, no background polling, no scheduled batch jobs) until the Creator **opens** the Gnome Guild chat panel from `/admin/gnome-guild`, `/workshop` guild area, or the world guild entrance.

When the panel opens, the server SHALL create or resume a **`gnome_guild_session`** for the Creator and allow agent invocations for that session.

When the panel closes, the server SHALL **first** persist the conversation to **`gnome_guild_log`**, flush in-session draft/work state, **then** end the session and mark gnome agents **dormant**. See `agent-life` chat panel close requirement.

The Creator's Son MUST NOT wake gnome agents on the Creator's behalf.

#### Scenario: Creator opens guild chat

- **WHEN** the Creator opens the Gnome Guild chat UI
- **THEN** the server marks the guild session active and gnome agents may respond to messages in that thread

#### Scenario: Creator closes guild chat

- **WHEN** the Creator closes the guild chat panel or leaves the guild route with the panel unmounted
- **THEN** the server writes messages to `gnome_guild_log`, saves draft/session snapshot, ends `gnome_guild_session`, and no further gnome Cursor API calls occur until the panel is opened again

#### Scenario: Login does not wake gnomes

- **WHEN** the Creator logs in but does not open the guild chat panel
- **THEN** gnome agents remain dormant and no guild Cursor API traffic is generated

### Requirement: Offline drafting with Son facilitation

When the Creator is offline, gnome agents SHALL remain **dormant** (no autonomous drafting). The Creator's Son MAY read guild history and leave comments for the Creator's return but SHALL NOT wake gnome agents or publish drafts without Creator approval.

#### Scenario: Son cannot wake gnomes while Creator away

- **WHEN** the Creator is offline and the Son opens or posts in guild-related UI
- **THEN** gnome agents are not invoked via Cursor API unless the Creator has an active guild session open

#### Scenario: Son continues thread while Creator offline

- **WHEN** the Creator is not present
- **THEN** the Son may comment on **existing** thread history and mark drafts `pending_approval`; gnomes do not produce new AI drafts until the Creator opens the guild chat panel

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

**`gnome_guild_log`** — all messages in the Gnome Guild group thread (Creator, Son, and three gnomes).

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

- **WHEN** `gnome_archivist` is invoked to analyze a published dungeon
- **THEN** the server supplies aggregated metrics from `dungeon_run_log` and optional samples from `dungeon_ui_log` without exposing logs to adventurers

#### Scenario: Guild messages persisted

- **WHEN** any participant posts in the Gnome Guild thread
- **THEN** the message is stored in `gnome_guild_log` with sender, timestamp, and body

### Requirement: Archivist-driven script maintenance

The archivist gnome SHALL support reviewing published dungeon catalog entries, comparing telemetry against design intent, and proposing hotfix drafts (returned to plot/engine gnomes). Hotfixes SHALL follow the same Creator approval flow as new scripts.

#### Scenario: Archivist flags overtuned node

- **WHEN** telemetry shows excessive hp loss or gold drain at a specific node across multiple runs
- **THEN** the archivist posts a summary in the guild thread referencing node id and suggested numeric adjustments for the engine gnome

#### Scenario: Hotfix draft for published dungeon

- **WHEN** gnomes produce a revision draft for an already published dungeon
- **THEN** the draft references the source dungeon id and version; publish replaces or versions the live script only after Creator approval; adventurers with in-progress runs on that dungeon remain on their pinned version until exit

#### Scenario: Hotfix does not affect active players

- **WHEN** a hotfix is published while one or more adventurers are mid-run on that dungeon
- **THEN** those runs complete on the script version they started with; the hotfix applies only to runs that begin after publish completes
