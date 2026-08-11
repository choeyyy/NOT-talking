## Status

**DISCUSSION** — 2026-08-11 用户提案；见 `discussion-log.md` §H。

## ADDED Requirements

### Requirement: Bounty board in big world

The system SHALL provide a **悬赏栏** (bounty board) accessible from the big world (`/world`) via a `bounty_board_entrance` interactable. Adventurers SHALL browse daily bounties, accept an open slot, and play a **short text script** (mini-run) with d100 checks that MAY add or deduct **persistent wallet gold**, with configured outcomes biased toward net gain.

#### Scenario: Enter bounty board from world

- **WHEN** an adventurer interacts with `bounty_board_entrance` in a world scene
- **THEN** a bounty board UI opens listing today's bounty slots and their status

#### Scenario: Accept open bounty

- **WHEN** an adventurer accepts an open bounty slot with sufficient daily AP and under their personal daily accept limit
- **THEN** the slot is marked taken, AP is deducted, a `bounty_run` starts, and acceptance is recorded for display on the board

#### Scenario: Cannot accept taken bounty

- **WHEN** an adventurer attempts to accept a bounty slot already taken by another adventurer
- **THEN** the accept action is rejected with themed feedback

### Requirement: Daily bounty limits

Bounty availability SHALL be limited on two axes (both configurable in manifest):

| Limit | Default (TBD in manifest) | Meaning |
|-------|---------------------------|---------|
| **Board pool** | e.g. N slots/day | How many bounties appear on the board each daily period |
| **Per adventurer accepts** | e.g. 3/day | How many bounties one adventurer may accept per daily period |

Both counters SHALL reset on the same daily boundary as action points (UTC+8 midnight unless configured otherwise).

#### Scenario: Board refreshes daily

- **WHEN** a new daily period begins
- **THEN** the bounty board repopulates from the configured pool and cleared slots become available again

#### Scenario: Personal accept cap reached

- **WHEN** an adventurer has reached their daily accept limit
- **THEN** further accept attempts are rejected even if open slots remain

### Requirement: Bounty run uses AP and shared d100 resolver

Accepting a bounty SHALL cost **daily action points** per `sanity-action-points` (same class as new dungeon entry; default **1 AP**). Bounty script nodes SHALL use the shared **`house-coc`** d100 resolver from `trpg-mechanics`. Gold outcomes SHALL apply to **persistent wallet gold** directly (not `run_gold`).

#### Scenario: Accept costs AP

- **WHEN** an adventurer accepts a bounty with remaining AP
- **THEN** entry AP is deducted and logged per `player-behavior-log`

#### Scenario: Accept blocked at zero AP

- **WHEN** an adventurer has 0 daily AP
- **THEN** bounty accept is rejected with themed feedback

#### Scenario: Bounty gold applied to wallet

- **WHEN** a bounty script outcome specifies `gold: +N` or `gold: -N`
- **THEN** persistent wallet gold is updated immediately on the server

### Requirement: Taken bounties visible on board with privacy

When a bounty slot is accepted, the board SHALL show that the slot is **taken** (or in progress / completed) and SHALL record **who** took it for audit. For adventurer-facing display, the taker's identity SHALL be filtered by `canSee(viewer, taker)` from `social-visibility`:

- If `canSee(viewer, taker)` is **true** → show taker display name (and optional character title if configured)
- If **false** → show a themed anonymous label (e.g. **「不相识的冒险者」**); MUST NOT expose user id, login id, or sprite
- **Creator** (`is_admin`) SHALL always see the real taker identity on the board and in admin audit

#### Scenario: Acquaintance sees taker name

- **WHEN** adventurer A views the bounty board and adventurer B (same party / mutual `canSee`) has taken a slot
- **THEN** the slot shows B's display name

#### Scenario: Stranger sees anonymous taker

- **WHEN** adventurer A views the board and adventurer C in another party has taken a slot
- **THEN** the slot shows the anonymous label and does not include C's user id or display name

#### Scenario: Creator sees all taker names

- **WHEN** the Creator views the bounty board or admin audit
- **THEN** every taken slot shows the real adventurer identity regardless of party

### Requirement: Bounty scripts from manifest

Bounty definitions SHALL be registered in a code manifest (`bounty-manifest`) with id, title, blurb, script reference (short JSON or shared dungeon script format with `kind=bounty`), and optional weight for daily pool selection. V1 MAY use static manifest deploy; Creator admin editors are optional later.

#### Scenario: Display bounty title on board

- **WHEN** the bounty board loads
- **THEN** each slot shows title, status, and taker display per privacy rules above

### Requirement: Bounty telemetry and behavior log

The system SHALL persist bounty acceptance and settlement for board display and audit:

| Store | Purpose |
|-------|---------|
| `bounty_board_state` (or equivalent) | Daily slot status, taker `user_id`, timestamps |
| `bounty_runs` | Per-run script progress and settlement |
| `player_behavior_log` | `bounty_accept`, `bounty_settle` events |

`bounty_settle` payload SHALL include gold delta, final d100 tier if applicable, and `bounty_id`.

#### Scenario: Accept logged

- **WHEN** an adventurer accepts a bounty
- **THEN** `player_behavior_log` records `bounty_accept` with `bounty_id`, slot id, and AP spent

#### Scenario: Settlement logged

- **WHEN** a bounty run completes (success or failure exit)
- **THEN** `bounty_settle` is logged with gold delta and board slot moves to completed state

### Requirement: Bounty distinct from full dungeons

Bounty runs SHALL NOT use `run_gold` accumulation or dungeon exit merge rules. They SHALL be shorter (target 2–5 nodes), MUST NOT drop soul potion, and MAY reuse the dungeon UI component with `run_kind=bounty` routing. Dead adventurers SHALL NOT accept bounties (same gate as dungeon entry).

#### Scenario: No run_gold on bounty

- **WHEN** a bounty outcome grants gold
- **THEN** wallet gold increases immediately without a separate merge step

#### Scenario: Dead adventurer blocked

- **WHEN** a dead adventurer attempts to accept a bounty
- **THEN** accept is rejected with guidance to revive first
