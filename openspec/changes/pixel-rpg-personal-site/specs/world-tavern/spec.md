## Status

**DISCUSSION** — 2026-08-11 用户提案；见 `discussion-log.md` §I。

## ADDED Requirements

### Requirement: Tavern scene with table seating

The big world SHALL include a tavern scene (manifest id **`tavern-hall`** only — no separate invented tavern display name in spec). Tavern scenes SHALL expose one or more **`tavern_table`** interactables, each with a stable `tableId`. Each table SHALL seat at most **2** adventurers concurrently. An adventurer SHALL **sit at a table** by interacting with a chair/seat at that table while in the tavern scene.

#### Scenario: Sit at tavern table

- **WHEN** an adventurer interacts with an empty seat at `tavern_table` `table-1` in `tavern-hall` and fewer than 2 adventurers are seated
- **THEN** the adventurer is seated at `table-1`, their seated state is broadcast to the other seated player if any, and table chat UI becomes available

#### Scenario: Table full

- **WHEN** an adventurer attempts to sit at a table that already has 2 seated adventurers
- **THEN** the sit action is rejected with themed feedback (e.g. table full)

#### Scenario: Leave table

- **WHEN** a seated adventurer chooses leave table, walks away beyond configured distance, or disconnects
- **THEN** they are unseated, removed from the table chat room, and any client-side table chat lines are cleared

### Requirement: Same-table chat bypasses stranger DM rules

Adventurers seated at the **same** `tavern_table` (`tableId` + `sceneId`) SHALL exchange **table chat** messages with each other **regardless of** `canSee()` / party rules. This SHALL NOT grant map-wide visibility, phone contact, gallery access, or persistent DM rights outside the table session.

#### Scenario: Strangers chat at same table

- **WHEN** adventurers A and B are in different parties, both seated at `table-1`, and A sends a table chat message
- **THEN** B receives the message in the table chat UI even though `canSee(A,B)` is false

#### Scenario: Strangers at different tables cannot table-chat

- **WHEN** A is seated at `table-1` and B is seated at `table-2`
- **THEN** A's table messages are not delivered to B

#### Scenario: Table chat does not enable persistent DM

- **WHEN** A and B chatted at the same tavern table as strangers and later A attempts `POST /api/chat/messages` to B outside the tavern table context **without** having completed the grilled duck-heart acquaintance ritual
- **THEN** the request is rejected per `player-chat` stranger rules (403)

#### Scenario: After heart ritual persistent DM enabled

- **WHEN** A and B complete the grilled duck-heart acquaintance ritual at the same table and later A sends persistent DM to B outside the tavern
- **THEN** the message is accepted per `player-chat` mutual acquaintance rules

### Requirement: Tavern bartender Li-Luang

Scene **`tavern-hall`** SHALL include a static bartender NPC **`li_luang`**, display name **`Li-Luang`** (English only), **grandmother**. Creator-configured fields in admin:

- **Dialogue:** what she **says to players** (includes her **drinks are AA** characterization)
- **Player address:** how she **calls players** — seed characterization **乖孙**

`mode: static` only. No example lines in this spec.

#### Scenario: Talk to Li-Luang at the bar

- **WHEN** an adventurer interacts with `li_luang` in `tavern-hall`
- **THEN** a JRPG dialogue shows her configured static lines from the server

#### Scenario: Li-Luang does not split bills server-side

- **WHEN** an adventurer reads Li-Luang's AA dialogue
- **THEN** no automatic gold split occurs; AA is flavor copy only unless a future tavern bill feature is added

### Requirement: Duck heart acquaintance ritual

Adventurers SHALL become **mutual acquaintances** (结识) outside Creator admin control **only** via the tavern **烤鸭心** (grilled duck heart) ritual per this requirement. Creator party assignment and direct acquaintance CRUD in admin remain separate overrides per `admin-creator` and `social-visibility`.

Ritual flow:

1. **Initiator** purchases **exactly 2** grilled duck heart items at the tavern menu (`tavern_grilled_duck_heart` ×2) with persistent gold; items are held as **pending table food** for the ritual (not generic inventory until ritual completes or cancels).
2. Initiator sends a **sit-together invite** to a target adventurer in the same `tavern-hall` scene: themed copy **「你要和我坐同桌吗？」** (configurable string id `tavern_sit_invite`).
3. Target **accepts** or declines; on accept, both MUST sit at the **same** `tavern_table` (max 2 seats).
4. While both are seated, **each** adventurer consumes **one** grilled duck heart from the pending ritual order (eat action).
5. On successful dual consumption, the server creates a **mutual** row in `user_acquaintances` (A↔B); `canSee(A,B)` and `canSee(B,A)` become true per `social-visibility`; `player_behavior_log` records `acquaintance_formed`.

#### Scenario: Purchase two hearts for ritual

- **WHEN** an adventurer buys 2 grilled duck hearts at the tavern menu with sufficient gold
- **THEN** gold is deducted, a pending ritual food bundle is created for that initiator, and no buff applies until eat step

#### Scenario: Sit-together invite sent

- **WHEN** an initiator with a pending 2-heart order invites adventurer B in `tavern-hall`
- **THEN** B receives a JRPG dialog with accept/decline; invite expires if either leaves the scene or initiator cancels

#### Scenario: Invite accepted and both seated

- **WHEN** B accepts and both sit at the same table with fewer than 2 other occupants
- **THEN** the table enters **ritual-ready** state linking A, B, and the pending heart order

#### Scenario: Both eat and become acquainted

- **WHEN** A and B each confirm eat while ritual-ready and seated
- **THEN** both hearts are consumed, each adventurer receives **bond duck heart stat bonuses** (two configured attrs per `world-tavern`), mutual `user_acquaintances` is created, and both may use persistent DM and map visibility outside the tavern

#### Scenario: Ritual fails if one leaves before eating

- **WHEN** one adventurer unseats or leaves `tavern-hall` before both eat, or the sit-together invite is declined or expires
- **THEN** the acquaintance ritual is cancelled, **no** `user_acquaintances` link is created, and any **uneaten** grilled duck hearts from that pending order remain with the **purchaser** as solo consumables (not refunded as gold)

#### Scenario: Solo eat hearts after failed ritual

- **WHEN** a ritual fails or is cancelled and the purchaser still holds one or two uneaten grilled duck hearts from that order
- **THEN** the purchaser MAY consume them while in `tavern-hall` (at the table or via menu eat action); each heart applies **solo eat** effects (**饱食度 / satiety** only) per manifest; eating both is allowed

#### Scenario: Already acquainted pair

- **WHEN** A and B are already mutual acquaintances and one attempts the heart ritual with the other
- **THEN** the ritual is rejected or downgraded to eat-only buff without duplicate acquaintance link

#### Scenario: Third player cannot join ritual table

- **WHEN** a table already has 2 seated adventurers in ritual-ready state
- **THEN** additional sit attempts are rejected as table full

### Requirement: Duck heart eat effects (bond vs solo)

Duck heart consumption SHALL apply **different effects** based on eat context:

| Context | When | Effect per heart |
|---------|------|------------------|
| **`bond_ritual`** | Both adventurers complete acquaintance ritual and each eats one heart while ritual-ready | **Two** configured persistent stat increases (two **different** keys — attrs and/or wallet fields per manifest `bond_duck_heart_bonus`); **not** satiety-only |
| **`solo`** | Ritual failed/cancelled leftovers eaten by purchaser; **or** adventurer buys and eats heart(s) without completing bond ritual | **`satiety` (饱食度)** increase only per manifest `solo_duck_heart_satiety` |

Bond ritual eat MUST NOT fall back to solo satiety-only effects. Solo eat MUST NOT grant bond dual-stat bonuses.

#### Scenario: Bond ritual eat grants two stats

- **WHEN** A and B each eat one heart during a successful acquaintance ritual
- **THEN** each adventurer receives the two configured bond stat deltas (e.g. two distinct `attrs` keys) and satiety is unchanged unless manifest also specifies a bond satiety delta (default **none**)

#### Scenario: Solo eat after failed ritual

- **WHEN** the purchaser eats leftover hearts after ritual cancel
- **THEN** each heart increases `satiety` only by configured amount; no bond stat bonuses apply

#### Scenario: Self-purchased heart without ritual

- **WHEN** an adventurer buys one or more grilled duck hearts at `tavern_menu` for personal consumption (not bound to an active ritual order) and eats them
- **THEN** each heart increases `satiety` only

#### Scenario: Satiety clamped

- **WHEN** solo eat would exceed `max_satiety`
- **THEN** `satiety` clamps to `max_satiety`

#### Scenario: Bond bonuses visible in HUD

- **WHEN** bond ritual eat applies attr changes
- **THEN** profile or sidebar HUD reflects updated attrs (and satiety if shown)

### Requirement: Tavern menu for grilled duck hearts

The tavern SHALL expose a **menu / counter** interactable (`tavern_menu`) in `tavern-hall` selling **`tavern_grilled_duck_heart`** for persistent gold. Ritual purchase requires quantity **2** in one order (or two sequential purchases bound to same pending ritual — manifest SHALL prefer single **2-duck-heart platter** SKU).

#### Scenario: Order from tavern menu

- **WHEN** an adventurer interacts with `tavern_menu` and orders grilled duck hearts
- **THEN** tavern catalog prices apply (not world-shop); purchase is logged as `tavern_food_purchase`

### Requirement: Table chat is ephemeral for adventurers

Tavern table chat SHALL be **ephemeral**. Messages MUST NOT be written to the persistent `messages` table and MUST NOT appear in adventurer phone chat, map DM history, or any reloadable conversation UI.

Server MAY hold table messages **in memory only** (or a short-TTL cache) for delivery to currently seated participants; on unseat, disconnect, or scene leave, adventurers MUST NOT retrieve prior table lines.

#### Scenario: No DB persistence for table chat

- **WHEN** an adventurer sends a tavern table chat message
- **THEN** the server does not insert a row into `messages` and does not expose the line via `GET /api/chat/history`

#### Scenario: Client clears table chat on leave

- **WHEN** an adventurer leaves the table or navigates away from `/world` / tavern scene
- **THEN** the table chat panel is cleared and prior lines are not restored on re-seat

#### Scenario: Re-seat starts fresh

- **WHEN** an adventurer sits again at the same table later
- **THEN** only new live messages from that seating session appear; earlier table chat from a previous session is not shown

### Requirement: Seated display names at table only

While seated at the same table, adventurers SHALL see **display names** (and optional character title) of other seated players at that table, even when `canSee` is false globally. This visibility SHALL be limited to the tavern table UI and seated roster; it SHALL NOT expose user ids in client APIs beyond what is required to send table messages, and SHALL NOT render stranger sprites on the wider map.

#### Scenario: Stranger sees tablemate name while seated

- **WHEN** A and B are strangers by party rules and both seated at `table-1`
- **THEN** A's table chat UI lists B's display name as a seated participant

#### Scenario: Stranger name hidden after unseat

- **WHEN** B unseats and A remains on the map in `tavern-hall` without global `canSee(A,B)`
- **THEN** A does not see B's sprite on the map and cannot open persistent DM with B

### Requirement: Table chat transport

Table chat SHALL use a dedicated realtime channel scoped to `room:tavern:{sceneId}:{tableId}`. Send API or WebSocket handler SHALL verify both sender and recipients are currently seated at that table in that scene.

#### Scenario: Send while seated

- **WHEN** a seated adventurer posts to table chat
- **THEN** all other currently seated adventurers at that table receive the message via the tavern table room

#### Scenario: Send rejected when not seated

- **WHEN** an adventurer not seated at `table-1` attempts to post to that table room
- **THEN** the server rejects the message with themed feedback

### Requirement: Tavern table chat distinct from oracle and Son

Tavern table chat UI SHALL be visually distinct from the global AI oracle, Creator's Son chat, and persistent adventurer DM dialogs.

#### Scenario: Table chat panel separate

- **WHEN** an adventurer opens table chat while seated
- **THEN** the UI is labeled as tavern/table conversation and does not merge into phone or sidebar DM threads

### Requirement: Creator audit policy for tavern table chat

Tavern table chat SHALL NOT appear in adventurer-visible history. Whether the Creator receives tavern table transcripts in admin audit is **TBD** (`discussion-log.md` §I **I3**); default implementation preference is **no long-term storage** (true ephemeral) unless Creator explicitly opts in later.

#### Scenario: Adventurer cannot query tavern history

- **WHEN** a non-admin adventurer requests tavern table chat history for any table
- **THEN** the server returns 403 or empty per ephemeral policy
