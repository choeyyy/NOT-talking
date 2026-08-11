## Status

**DISCUSSION** — 2026-08-11 用户提案；与地精协会对称；见 `discussion-log.md` §M、§N。**长身人运维常启**（2026-08-11 拍板，与之子同级）。

## ADDED Requirements

### Requirement: Tall Folk guild for world engineering

The system SHALL expose a **Tall Folk Guild** (长身人修会) for the Creator to maintain **world-related runtime behavior**—API rules, scene/NPC config, feature flags, bugfix patches—parallel to the Gnome Guild's **content** (dungeon narrative JSON).

The guild SHALL consist of exactly **three** persona agents with distinct `agent_bindings` (ids TBD, e.g. `tall_diagnostician`, `tall_engineer`, `tall_releaser`).

#### Scenario: Creator opens tall folk guild

- **WHEN** the Creator navigates to `/admin/tall-folk` (or linked module from admin hub)
- **THEN** the UI shows guild chat, open **issue reports**, **runtime patch drafts**, and deploy queue status

### Requirement: Tall Folk code company visible in big world

The big world (`/world`) SHALL display a **Tall Folk code company** (长身人代码公司 / 长身人修会) interactable — visible sprite, door, sign, or scene facade that **all logged-in adventurers** can see and walk to. This world presence is **flavor and world-building**; it is not hidden behind `canSee` party rules unless configured otherwise.

Functional Tall Folk tools (chat, patch drafts, deploy queue) remain **Creator-only** via `/admin/tall-folk` or the world entrance when the user is the Creator.

#### Scenario: Adventurer sees tall folk company in world

- **WHEN** any logged-in adventurer enters a scene that contains a `tall_folk_guild_entrance` object
- **THEN** the code-company facade is rendered like other world landmarks

### Requirement: Adventurers turned away at the door

Adventurers MUST NOT enter the functional Tall Folk Guild (chat, patch drafts, deploy approve). When an adventurer attempts to enter via the world interactable or any non-Creator API, the system SHALL show a **JRPG-style refusal dialog** with the **canonical static line**:

**「非法闯入请刷卡。」**

This line SHALL be shown **as-is** (no AI generation required for adventurer refusal). Tall Folk refusal MUST NOT expose engineering spoilers or guild internals.

#### Scenario: Adventurer rejected at world entrance

- **WHEN** a non-Creator adventurer interacts with `tall_folk_guild_entrance`
- **THEN** the dialog shows **「非法闯入请刷卡。」**; Tall Folk chat and patch UI do not open

#### Scenario: Rejection logged

- **WHEN** an adventurer receives a tall folk refusal at the world entrance
- **THEN** `player_behavior_log` records `tall_folk_guild_rejection` with source `static`

#### Scenario: Creator enters from world

- **WHEN** the Creator interacts with `tall_folk_guild_entrance`
- **THEN** the full Tall Folk Guild UI opens per this spec (same as navigating to `/admin/tall-folk`)

### Requirement: Three-tier change model (hot / warm / cold)

Tall Folk agents MUST classify every proposed fix into one tier. **Direct in-memory modification of running TypeScript or React bundles in production is FORBIDDEN.**

| Tier | Name | Examples | Apply mechanism | Downtime |
|------|------|----------|-----------------|----------|
| **T0 Hot** | Runtime config | Scene manifest rows, NPC dialog patches, `feature_flags`, API rate limits, dungeon loader cache invalidate | Write DB `runtime_patches` / existing registries; server **cache invalidate** | None |
| **T1 Warm** | Worker reload | Agent prompt updates, queue worker logic, WS fan-out rules | Restart **`agent-worker`** or **`ws-gateway`** process only; web app keeps serving HTTP | Seconds; WS reconnect |
| **T2 Cold** | Code deploy | Next.js routes, React components, schema migration, lib bugfixes | Tall Folk outputs **patch artifact** (diff/PR); Creator **approves** → CI build → **rolling replace** `web` container | ~30s rolling; in-flight dungeon runs pinned |

Gnome **dungeon script publish** is **T0 only** (subset of runtime registry). Tall Folk **engine** gnome-analog MUST NOT merge dungeon narrative authorship—that remains Gnome Guild.

#### Scenario: Hot patch scene door target

- **WHEN** the tall engineer publishes an approved T0 patch changing a portal target scene id
- **THEN** the next world load reads DB config without process restart

#### Scenario: Cold patch requires deploy queue

- **WHEN** a fix requires editing `app/api/dungeons/resolve/route.ts`
- **THEN** the tall releaser creates a deploy draft linked to a git patch; live code unchanged until Creator approves T2 deploy

#### Scenario: In-flight dungeon run during T0 script hotfix

- **WHEN** a T0 dungeon script update publishes while runs are active
- **THEN** existing runs keep pinned `script_version`; only new runs load the latest version (same rule as gnome publish)

### Requirement: Tall Folk MUST NOT auto-deploy code

Tall Folk agents MAY propose T2 patches and run validation (lint, schema check, dry-run tests) but MUST NOT push to production or restart the `web` container without explicit Creator approval on the deploy queue.

#### Scenario: Engineer proposes API fix

- **WHEN** `tall_engineer` generates a patch for a wallet bug
- **THEN** status is `pending_creator_deploy` until the Creator clicks approve deploy

### Requirement: Process split for independent restart (recommended V2+)

To allow **warm** restarts without killing the whole site, deployment SHOULD split into at least:

| Process | Responsibility | Restart impact |
|---------|----------------|----------------|
| **`web`** | Next.js HTTP, SSR, most API routes | Rolling deploy; brief session stickiness |
| **`ws-gateway`** | WebSocket presence, tavern rooms, map broadcast | Clients reconnect; HTTP unaffected |
| **`agent-worker`** | Cursor API jobs: gnomes, tall folk, son, oracle queue | AI briefly unavailable; gameplay HTTP OK |

V1 MAY run monolith (single container) with the understanding that **T2 cold deploy restarts everything**; Tall Folk guild SHOULD still output tier tags so migration to split processes is straightforward.

#### Scenario: Agent worker restart during tall folk prompt update

- **WHEN** the Creator approves a T1 worker config change
- **THEN** only `agent-worker` restarts; adventurers can still load `/world` and `/home` over HTTP

### Requirement: Diagnostics from logs

The diagnostician tall folk SHALL read Creator-visible logs (`player_behavior_log`, `dungeon_run_log`, admin audit, server error summaries) to open **issue tickets** linked to proposed T0/T1/T2 fixes.

#### Scenario: Archivist analog finds spike in 500 errors

- **WHEN** error rate on `/api/dungeons/*` exceeds threshold in admin summary
- **THEN** `tall_diagnostician` opens an issue draft in the guild thread with log excerpts and suggested tier

### Requirement: Adventurers forbidden from tall folk APIs

Only `is_admin=true` MAY call tall folk chat, patch draft, or deploy approve APIs.

### Requirement: Tall Folk ops always running

Unlike Gnome Guild agents (dormant until the Creator opens their chat panel), **Tall Folk ops** (长身人运维 — the three tall folk persona bindings as the site's **technical maintenance team**) SHALL be **always started** with the main application: bindings are loaded at process boot, tall-folk maintenance routes remain available whenever the site is up, and the agent-worker (if split) MUST keep Tall Folk ops **hot** without requiring the Creator to open a panel first.

The Creator still **opens `/admin/tall-folk` or the world entrance** to chat and review patch/deploy drafts; "always running" means the **backend ops personas are never dormant** and MAY run background maintenance (log diagnostics, issue drafts) while the Creator is offline or the UI is closed.

When the Creator **closes** the Tall Folk chat panel, the server SHALL persist to `tall_folk_guild_log` and flush in-session draft state per `agent-life`, **then** end the **UI session only** — Tall Folk ops bindings **remain resident**.

Background Cursor API for scheduled diagnostics MUST pass through `AgentRouter` and respect `agent-safety` rate limits (separate from gnome guild session caps).

#### Scenario: Site up with Creator offline

- **WHEN** the main application is running and error logs exceed threshold while the Creator is offline
- **THEN** `tall_diagnostician` MAY open or update issue drafts in the background without any Creator UI session

#### Scenario: Creator opens tall folk without wake step

- **WHEN** the Creator opens `/admin/tall-folk` after site boot
- **THEN** tall folk agents are immediately available for chat and patch work — no dormancy gate

#### Scenario: Creator closes tall folk chat panel

- **WHEN** the Creator closes the Tall Folk chat UI
- **THEN** messages and draft snapshot are persisted, the UI session ends, and tall folk ops **remain always-on** for background work and the next panel open

#### Scenario: Adventurer API forbidden

- **WHEN** a non-admin calls `POST /api/admin/tall-folk/deploy/approve`
- **THEN** the server returns 403
