## ADDED Requirements

### Requirement: Text script dungeon gameplay

Dungeons SHALL be played as interactive text scripts (文字剧本) rendered in the dungeon tab. Each script SHALL consist of nodes with narrative text, optional choices, optional d100 checks, and effects on player stats.

#### Scenario: Start dungeon script

- **WHEN** an adventurer enters `/dungeon/[id]`
- **THEN** the first script node text is displayed in a JRPG log-style UI

#### Scenario: Advance by choice

- **WHEN** a node presents choices and the adventurer selects one
- **THEN** the next configured node loads with its narrative text

### Requirement: d100 roll checks

When a script node includes a check, the system SHALL roll an integer from 1 to 100 inclusive and resolve graded outcomes against a configured difficulty (DC) and optional stat modifier.

#### Scenario: Player triggers roll node

- **WHEN** an adventurer reaches a node with a d100 check and confirms the roll action
- **THEN** the system generates a roll 1–100, displays the value, and resolves success tier text

#### Scenario: Graded outcomes

- **WHEN** a roll is resolved
- **THEN** the outcome tier (e.g., critical success, success, failure, critical failure) is determined per dungeon script configuration and shown to the player

### Requirement: HP uses persistent wallet during dungeon

Dungeon gameplay SHALL use the adventurer's persistent wallet `hp` and `max_hp`. Entering a dungeon MUST NOT reset or fork HP into a separate run pool. HP changes from script nodes and roll outcomes SHALL apply immediately to persistent `hp`.

#### Scenario: Enter dungeon with current wallet HP

- **WHEN** an adventurer with wallet `hp=35` enters `/dungeon/[id]`
- **THEN** the dungeon UI shows HP 35 and uses wallet values for all checks and effects

#### Scenario: Lose HP on failed check

- **WHEN** an outcome specifies `hp: -10` and the adventurer has sufficient HP
- **THEN** persistent wallet HP decreases by 10 and the sidebar HUD updates

#### Scenario: HP reaches zero

- **WHEN** persistent wallet HP reaches 0 or below during a dungeon run
- **THEN** the run ends, run gold is not merged (default), the adventurer is marked dead, and the client is sent to the big-world revival platform

#### Scenario: Dead adventurer cannot re-enter dungeon

- **WHEN** a dead adventurer attempts to enter a dungeon
- **THEN** the system blocks entry with themed guidance to revive at the revival platform

#### Scenario: HP persists after leaving dungeon

- **WHEN** an adventurer exits a dungeon with reduced wallet HP
- **THEN** the reduced HP remains in the wallet for shop visits and future dungeon entries

### Requirement: Performance affects attributes and dungeon exp

Script nodes and roll outcomes MAY apply changes to persistent adventurer attributes (`attrs`) and to run-scoped `dungeon_exp`. These values SHALL influence which ending the run resolves to.

#### Scenario: Gain attribute from outcome

- **WHEN** an outcome specifies `attrs: { wit: +1 }`
- **THEN** persistent wallet attributes are updated immediately

#### Scenario: Gain dungeon exp

- **WHEN** an outcome specifies `dungeon_exp: +10`
- **THEN** the current run's dungeon exp increases by 10

#### Scenario: Ending gated by performance

- **WHEN** an adventurer reaches an ending node requiring `dungeon_exp >= 50`
- **THEN** the ending is available only if run dungeon exp meets the threshold; otherwise a fallback ending node is used if configured

#### Scenario: Multiple endings

- **WHEN** a dungeon script defines multiple ending nodes with different conditions on `dungeon_exp`, `attrs`, or run flags
- **THEN** the server resolves exactly one ending using configured priority rules

### Requirement: Critical success may award soul potion

On exit, when the resolved ending tier is critical success, the server SHALL invoke the soul potion drop roll defined in `agent-life` before clearing the run.

#### Scenario: Exit summary shows potion drop

- **WHEN** critical success exit awards a soul potion
- **THEN** the exit UI includes soul potion loot alongside run gold merge results

### Requirement: Run gold during dungeon

Script nodes and roll outcomes SHALL accumulate dungeon loot in `run_gold` separate from persistent wallet gold until successful exit.

#### Scenario: Gain gold in dungeon

- **WHEN** an outcome specifies `gold: +25`
- **THEN** run gold increases by 25 and persistent wallet gold is unchanged until exit

### Requirement: Carry gold out of dungeon

Gold earned during a dungeon run SHALL be merged into the adventurer's persistent wallet when the run completes successfully via an exit node. Gold MUST NOT be lost on successful completion.

#### Scenario: Successful exit with loot

- **WHEN** an adventurer reaches a configured exit node with 80 run gold
- **THEN** 80 gold is added to persistent wallet and the run state is cleared

#### Scenario: Defeat carries partial rules

- **WHEN** an adventurer is defeated mid-run
- **THEN** gold handling follows script or global rule (default: no gold awarded on defeat unless node specifies)

### Requirement: Dungeon run state

The system SHALL persist in-progress dungeon run state (current node, run gold, dungeon_exp, run flags) per user per dungeon id until completion, defeat, or abandon. HP and persistent `attrs` use wallet values and are not duplicated on the run record.

#### Scenario: Resume dungeon

- **WHEN** an adventurer re-enters an in-progress dungeon
- **THEN** the run resumes from the saved node with current wallet HP and attrs, plus saved run gold and dungeon_exp

#### Scenario: Abandon run

- **WHEN** an adventurer abandons a dungeon from the UI
- **THEN** run state is cleared without awarding run gold to persistent wallet

### Requirement: Dungeon tab and world entrance

The system SHALL provide `/dungeon` and `/dungeon/[id]` routes. World scenes SHALL link via `dungeon_entrance` interactables. Entering a dungeon SHALL leave world map presence.

#### Scenario: Enter from world

- **WHEN** an adventurer uses a permitted dungeon entrance in `/world`
- **THEN** the app navigates to `/dungeon/[id]` and world clients despawn their sprite

#### Scenario: Exit to world

- **WHEN** an adventurer completes or exits a dungeon via exit node
- **THEN** the app returns to `/world` and world presence may resume

### Requirement: Dungeon script registry

Dungeons SHALL resolve from a **runtime catalog** backed by the database. A code-shipped bootstrap sample MAY seed the first row(s) via migration; it MUST NOT be the only path for adding or updating playable scripts after deploy.

**`dungeon_scripts`** (live catalog) SHALL store at minimum: `id`, `label`, `script_json`, `version`, `is_published`, `published_at`, optional `source_draft_id`.

**`dungeon_entrances`** (optional runtime entrances) SHALL store: `scene_id`, position, `dungeon_id`, `label`, `is_active`. World clients SHALL merge Tiled `dungeon_entrance` objects with active DB entrances when listing enterable dungeons.

At least one sample script SHALL be playable in V1 (via seed or bootstrap).

#### Scenario: Load published script without restart

- **WHEN** a published script exists in `dungeon_scripts` and an adventurer enters `/dungeon/[id]`
- **THEN** the server loads `script_json` from the database via `DungeonScriptLoader` without requiring application restart or code redeploy

#### Scenario: Unknown dungeon id

- **WHEN** an unregistered or unpublished dungeon id is requested
- **THEN** a themed not-found page is shown

#### Scenario: Publish invalidates loader cache

- **WHEN** a script is published or hotfixed to `dungeon_scripts`
- **THEN** any in-memory script cache for that `dungeon_id` is invalidated so subsequent new runs see the updated version immediately

#### Scenario: Active run pins script version

- **WHEN** a dungeon run is in progress and a newer script version is published for the same `dungeon_id`
- **THEN** the in-progress run continues using the `script_version` captured at run start and MUST NOT switch to the new script mid-run; only new runs load the latest published version

#### Scenario: No mid-run script swap

- **WHEN** the server resolves the next node for an active `dungeon_runs` row
- **THEN** it loads script JSON for that run's pinned `script_version`, not the current catalog head version

### Requirement: Spirit and admin publish path

Script publication from the Spirit Guild or Creator admin SHALL write only to the runtime catalog (`dungeon_scripts`, optional `dungeon_entrances`) and related announcements. Publication MUST NOT require modifying repository source files or restarting the application process.

#### Scenario: Engine spirit draft stays in DB

- **WHEN** `spirit_engine` completes a script draft
- **THEN** the output is stored in `dungeon_script_drafts` only; no TypeScript manifest or filesystem deploy artifact is produced

#### Scenario: Approved publish is atomic and live

- **WHEN** the Creator approves a pending draft for publish
- **THEN** the server validates JSON schema, upserts `dungeon_scripts` with incremented version, optionally upserts entrances, upserts announcement, marks draft published, and invalidates loader cache in one transaction without restart

### Requirement: Dungeon run telemetry logging

The system SHALL persist structured dungeon telemetry for Creator audit and future archivist analysis (see `spirit-guild`). Logging SHALL occur server-side on each meaningful run event.

**`dungeon_run_log`** entries SHALL include at minimum: run id, user id, dungeon id, node id, event type (e.g., `dice_roll`, `hp_delta`, `gold_delta`, `attr_delta`, `exit_settlement`), payload JSON, and timestamp.

**`dungeon_ui_log`** entries SHALL record each JRPG log line shown to the player during a run (text body, optional choice id, run id, timestamp).

Adventurers MUST NOT retrieve these logs via API or UI.

#### Scenario: Log dice roll server-side

- **WHEN** the server resolves a d100 check for a dungeon run
- **THEN** a `dungeon_run_log` row records roll value, outcome tier, and node id

#### Scenario: Log hp or gold change

- **WHEN** a script outcome applies hp or gold change to wallet or run_gold
- **THEN** a `dungeon_run_log` row records before/after or delta and source node id

#### Scenario: Log exit settlement

- **WHEN** a run exits with a resolved ending
- **THEN** `dungeon_run_log` records ending tier, merged run_gold, dungeon_exp snapshot, and loot flags

#### Scenario: Log UI narrative line

- **WHEN** narrative or roll summary text is sent to the client for display in the dungeon log UI
- **THEN** the same text is appended to `dungeon_ui_log` for that run

