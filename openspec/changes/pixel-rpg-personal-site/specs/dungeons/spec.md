## ADDED Requirements

### Requirement: Dungeon entry costs action points

Entering or starting a new dungeon run SHALL cost **daily action points** per `sanity-action-points`. Continuing an in-progress run on the same day MAY be exempt from additional entry cost (configurable).

#### Scenario: Enter dungeon with AP

- **WHEN** an adventurer enters a dungeon with sufficient daily AP
- **THEN** entry AP is deducted and the run starts or resumes

#### Scenario: Enter dungeon without AP

- **WHEN** an adventurer attempts new dungeon entry with 0 daily AP
- **THEN** entry is rejected with themed feedback

### Requirement: Text script dungeon gameplay

Dungeons SHALL be played as interactive text scripts (文字剧本) rendered in the dungeon tab. Each script SHALL consist of nodes with narrative text, optional choices, optional d100 checks, and effects on player stats.

#### Scenario: Start dungeon script

- **WHEN** an adventurer enters `/dungeon/[id]`
- **THEN** the first script node text is displayed in a JRPG log-style UI

#### Scenario: Advance by choice

- **WHEN** a node presents choices and the adventurer selects one
- **THEN** the next configured node loads with its narrative text

### Requirement: d100 roll checks

When a script node includes a check, the system SHALL roll an integer from 1 to 100 inclusive and resolve graded outcomes using the shared **`house-coc`** profile in `trpg-mechanics`.

Check nodes SHALL declare at minimum `dc`, optional `stat` modifier, and an `outcomes` object keyed by canonical tier names. Ending nodes SHOULD use the same tier keys when gated on crit results (e.g., soul potion drop on exit `crit_success`).

#### Scenario: Player triggers roll node

- **WHEN** an adventurer reaches a node with a d100 check and confirms the roll action
- **THEN** the system generates a roll 1–100, resolves tier via shared resolver, displays roll value and tier label, and applies the matching outcome branch

#### Scenario: Graded outcomes

- **WHEN** a roll is resolved
- **THEN** the outcome tier (`crit_success`, `extreme_success`, `hard_success`, `success`, `failure`, `crit_failure`) is determined by the shared resolver and shown to the player

### Requirement: Party dungeon runs with acquainted players

Adventurers MAY enter the **same** dungeon script together as a **party run** when all members are **mutual acquaintances** (`canSee` both ways). Dungeons SHALL **not** ship separate solo vs multiplayer script ids; one published script serves all party sizes. When `party_size > 1`, the server SHALL merge **party check rules** (harder DC) with optional **`partyVariants`** on each node — alternate copy, choices, effects, and branches authored for multi-member context (see below). Gnome plot/engine agents MUST co-author these variants per `gnome-guild`.

**Party limits (default, manifest-overridable):** min 1, max **4** members per run. Non-acquainted invitees MUST be rejected.

#### Scenario: Solo enter unchanged

- **WHEN** an adventurer enters a dungeon alone
- **THEN** the run behaves as today with `party_size = 1` and no party DC adjustment unless the node sets explicit solo overrides

#### Scenario: Party invite at entrance

- **WHEN** an adventurer at a dungeon entrance invites mutual acquaintances and all accept
- **THEN** a shared `dungeon_party_run` starts with pinned `script_version`; each member pays entry AP (default 1 AP each); all share the same current node

#### Scenario: Stranger cannot join party run

- **WHEN** user A invites user B to a dungeon party and `canSee(A,B)` is false
- **THEN** the invite is rejected with themed feedback

#### Scenario: Shared progression

- **WHEN** the party reaches a choice or check node
- **THEN** all members see the same narrative advance; check nodes collect one roll per present member before resolving the party outcome

### Requirement: Party check on d100 nodes

Check nodes MAY include an optional **`partyCheck`** block. When `party_size > 1` and `partyCheck.enabled` is true (default **true** when block omitted and global default enabled), the server SHALL:

1. Use the node's **`dc`** as **`baseDc`** (same number for solo preview and party display).
2. Compute **`soloEffectiveDc`** per member = `baseDc` ± that member's stat modifier.
3. Compute **`partyEffectiveDc`** = `baseDc` + stat modifier of the **acting member** (or **best stat among party** if `partyCheck.statMode: "best"`) + **`dcDeltaFromPartySize`**.
4. Roll **once per party member** (each uses their own wallet `attrs` for stat mod).
5. Resolve **party outcome tier** from individual tiers via `partyCheck.resolution`.
6. Display in UI **both** solo preview and full party breakdown (see scenarios).

**Default `dcDeltaFromPartySize` (global manifest `party-check-manifest`, overridable per node):**

| `party_size` | Default Δ to effective DC |
|--------------|---------------------------|
| 1 | 0 |
| 2 | **+5** |
| 3 | **+10** |
| 4 | **+15** |

Positive Δ raises effective DC — **more party members make checks harder**. Party difficulty is **not** DC alone; nodes SHOULD also define **`partyVariants`** for narrative and mechanical differences when multiple adventurers face the same beat.

**`partyVariants` resolution:** When `party_size >= 2`, the server selects the variant with the **largest** `minPartySize` such that `minPartySize <= party_size`. If none match, the base node fields apply. Variant fields **override or merge** with the base node as documented per field type.

| Field (in variant) | Behavior |
|--------------------|----------|
| `text` | Replaces base narrative text for party |
| `choices` | Replaces base choices entirely when present |
| `onEnter` | Additional or replacement immediate effects (`hp`, `gold`, `attrs`, `flags`) before roll/choice |
| `partyCheck` | Overrides base `partyCheck` for this node |
| `outcomes` | On check nodes, merges with or replaces tier outcomes for party context |
| `next` | On linear nodes, override next node id |

#### Scenario: Party variant text at passage node

- **WHEN** a party of 2 enters a node with base text for solo and a `partyVariants` entry `{ "minPartySize": 2, "text": "两人并排通过时横梁吱呀作响……" }`
- **THEN** all members see the party variant text, not the solo base text

#### Scenario: Party variant adds onEnter hazard

- **WHEN** a party of 3 triggers a variant with `onEnter: { "hp": -2, "applyEffects": "each" }`
- **THEN** each member loses 2 wallet HP before any check or choice on that node

#### Scenario: Party of 4 uses highest matching variant

- **WHEN** variants exist for `minPartySize` 2 and 3 only and party size is 4
- **THEN** the server applies the `minPartySize: 3` variant (largest matching threshold)

#### Scenario: Solo ignores partyVariants

- **WHEN** `party_size === 1`
- **THEN** base node fields apply; `partyVariants` are ignored

**`partyCheck.resolution` modes (enum):**

| Mode | Party tier = |
|------|----------------|
| `best_roll` (default) | Best tier among members (crit_success > extreme_success > … > crit_failure) |
| `worst_roll` | Worst tier among members |
| `majority_success` | `success` if ≥ half of members achieve `success` or better; else `failure` |
| `any_success` | `success` if any member achieves `success` or better; else `failure` |

#### Scenario: UI shows solo preview and party rolls on same base DC

- **WHEN** a party of 2 reaches a check with `baseDc: 60` and default party Δ
- **THEN** the dungeon log shows: (a) **单人预览** — each viewer's hypothetical solo line using `soloEffectiveDc` at `baseDc 60`; (b) **队伍检定** — each member's actual roll against `partyEffectiveDc` (e.g. **65** for 2 players); (c) **队伍结果** — resolved party tier and applied outcome branch

#### Scenario: Solo run hides party panel

- **WHEN** `party_size === 1`
- **THEN** only the single roll against `soloEffectiveDc` is shown; party panel is omitted

#### Scenario: Party check logged per member

- **WHEN** a party check resolves
- **THEN** `dungeon_run_log` records one `dice_roll` row per member with `baseDc`, `soloEffectiveDc`, `partyEffectiveDc`, roll, tier, and final `partyTier`

#### Scenario: Outcome effects on party

- **WHEN** a party check outcome specifies `hp: -10` and `partyCheck.applyEffects: "each"` (default)
- **THEN** each member's wallet HP decreases by 10 unless the outcome overrides `applyEffects: "roller"` (only rolling member) or `leader`

#### Example narrative node with partyVariants

```json
{
  "id": "narrow-gap",
  "type": "narrative",
  "text": "你侧身挤过石缝。",
  "next": "chamber",
  "partyVariants": [
    {
      "minPartySize": 2,
      "text": "两个人先后挤过，第二人经过时石缝刮破了背包。",
      "onEnter": { "run_gold": -5, "applyEffects": "leader" }
    },
    {
      "minPartySize": 3,
      "text": "三个人无法同时通过；你们轮流侧行，头顶不断落下碎石。",
      "onEnter": { "hp": -2, "applyEffects": "each" },
      "next": "chamber-noisy"
    }
  ]
}
```

#### Example check node (authoring)

```json
{
  "id": "rusty-lock",
  "type": "check",
  "text": "一把锈锁挡住了去路。",
  "dc": 60,
  "stat": "dex",
  "partyCheck": {
    "enabled": true,
    "dcDeltaPerExtraMember": 5,
    "resolution": "best_roll",
    "showSoloPreview": true
  },
  "partyVariants": [
    {
      "minPartySize": 2,
      "text": "两个人同时动手撬锁，金属声在通道里回荡——更容易惊动守卫。",
      "partyCheck": { "dcDeltaPerExtraMember": 8 },
      "outcomes": {
        "failure": { "next": "alarm-loud", "hp": -8, "applyEffects": "each" }
      }
    }
  ],
  "outcomes": {
    "success": { "next": "door-open", "gold": 10 },
    "failure": { "next": "alarm", "hp": -5 }
  }
}
```

#### Scenario: Publish validates partyCheck and partyVariants schema

- **WHEN** a draft node includes unknown `partyCheck.resolution` or invalid `partyVariants.minPartySize`
- **THEN** publish validation fails with a schema error

#### Scenario: Co-op dungeon warns on sparse partyVariants

- **WHEN** script root has `supportsParty: true` and fewer than the configured minimum nodes define `partyVariants`
- **THEN** publish returns a Creator-visible warning per `gnome-guild` co-op checklist (soft gate)

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

Script publication from the Gnome Guild or Creator admin SHALL write only to the runtime catalog (`dungeon_scripts`, optional `dungeon_entrances`) and related announcements. Publication MUST NOT require modifying repository source files or restarting the application process.

#### Scenario: Engine gnome draft stays in DB

- **WHEN** `gnome_engine` completes a script draft
- **THEN** the output is stored in `dungeon_script_drafts` only; no TypeScript manifest or filesystem deploy artifact is produced

#### Scenario: Approved publish is atomic and live

- **WHEN** the Creator approves a pending draft for publish
- **THEN** the server validates JSON schema, upserts `dungeon_scripts` with incremented version, optionally upserts entrances, upserts announcement, marks draft published, and invalidates loader cache in one transaction without restart

### Requirement: Creator manual script edit in admin (T0 hot update)

The Creator SHALL edit dungeon scripts in admin **without** going through gnome chat when desired. This uses the same runtime catalog as gnome publish (**T0** — DB + cache invalidate, no restart).

| Action | Where | Result |
|--------|-------|--------|
| **Edit draft** | `/admin/gnome-guild` or **`/admin/dungeons`** | Updates `dungeon_script_drafts`; not live until publish |
| **Publish / hotfix** | Same + confirm action | Upserts `dungeon_scripts` (`version++`), invalidate loader; **new runs only** |
| **Adjust live script** | Edit published row or draft → publish | Same hotfix rules; in-progress runs stay pinned |

Gnome-authored and Creator-hand-edited scripts share one schema validator (`script-schema.ts` / `house-coc` tiers). The Creator MAY change any field gnomes can (nodes, DC, text, rewards, `partyVariants`, etc.).

#### Scenario: Creator edits gnome draft before publish

- **WHEN** the Creator opens a `dungeon_script_drafts` row in admin and saves JSON changes
- **THEN** the draft updates; live `dungeon_scripts` unchanged until Creator publish confirm

#### Scenario: Creator hotfixes published script without gnomes awake

- **WHEN** the Creator edits and publishes a new version of an existing `dungeon_scripts` row from admin while gnome guild chat is closed
- **THEN** `dungeon_scripts.version` increments, cache invalidates, and new dungeon runs load the updated script immediately

#### Scenario: Creator hotfix does not disrupt active run

- **WHEN** the Creator publishes a script hotfix while adventurers are mid-run on that dungeon
- **THEN** those runs keep pinned `script_version`; only runs started after publish use the new version

#### Scenario: Invalid Creator edit blocked

- **WHEN** the Creator saves script JSON that fails schema or tier validation
- **THEN** publish is rejected with errors; live catalog is not updated

The system SHALL persist structured dungeon telemetry for Creator audit and future archivist analysis (see `gnome-guild`). Logging SHALL occur server-side on each meaningful run event.

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

