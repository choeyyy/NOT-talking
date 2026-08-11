## ADDED Requirements

### Requirement: Agent binding as core abstraction

The system SHALL represent all persona agents (except the separate oracle tool) using `agent_bindings` records keyed by `target_type` and `target_id`. Chat SHALL route through a shared server-side Cursor API proxy using the binding's `system_prompt` and `model`.

**Gnome Guild agents:** Cursor API calls for gnome bindings MUST occur only while the Creator has an **active gnome guild chat session** open. **Login alone MUST NOT wake gnome agents.**

**Tall Folk ops (长身人运维):** SHALL be **always running** with the main app — never dormant. Tall Folk maintenance routes and background diagnostics remain available when the site is up; the Creator opens `/admin/tall-folk` to chat, but there is no wake-up step like gnomes. Tall Folk behavior is constrained by `agent-safety` (no auto-deploy, Creator approve for T2, rate limits on background jobs).

**Creator's Son:** SHALL be **always running** with the main app — never dormant. `/api/son/chat` is always available when the site is up; adventurers open the Son UI to message, but the Son backend does not require a wake-up step. Son behavior is constrained by `agent-safety` (no publish, grant limits, no admin escalation).

**Other player-initiated agents (awakened creations, oracle):** Invoked when the user opens the chat UI and sends a message (or equivalent explicit action). All routes through `agent-safety` AgentRouter.

**Ad-hoc agent group chat is OUT OF SCOPE:** The Creator MUST NOT assemble arbitrary multi-agent group threads by picking bindings (Son + gnomes + tall folk + NPCs, etc.). Persona chat is limited to **fixed guild threads** (Gnome Guild, Tall Folk Guild) and **1:1** routes per binding. See `discussion-log.md` §R.

#### Scenario: Creator cannot create custom agent group

- **WHEN** the Creator attempts to create a chat room with a custom set of agent bindings
- **THEN** the feature is unavailable; the server exposes only fixed guild threads and per-binding 1:1 chat endpoints

### Requirement: Chat panel close flushes then sleeps

When any agent **chat panel** closes (guild, Son, oracle, awakened creation), the client SHALL notify the server (e.g., `POST .../session/close` or reliable `sendBeacon`). The server SHALL **before** marking the session inactive:

1. **Persist** all messages from the current session to the appropriate server log table (see below)
2. **Flush** in-session work product — e.g., link latest draft revision, pending publish/deploy proposals, session summary metadata
3. **Then** end the **UI session** (gnome agents → **dormant**; Son and **Tall Folk ops** → backend remains always-on; oracle → UI session closed)

Guild agents (**gnomes only**) MUST NOT enter dormant state until steps 1–2 complete successfully or fail with logged error (retry on next open). Tall Folk ops and Son backends are unaffected by UI session close.

| Chat UI | Server log (Creator-readable where noted) |
|---------|-------------------------------------------|
| Gnome Guild | `gnome_guild_log` |
| Tall Folk | `tall_folk_guild_log` |
| Creator's Son | Son chat log (Creator audit) |
| Oracle | Oracle chat log (per-user, Creator audit) |
| Awakened creation | Creation owner + Creator audit policy |

Adventurers MUST NOT read these agent chat logs via API; see `player-chat` history restriction.

#### Scenario: Creator closes gnome guild chat

- **WHEN** the Creator closes the Gnome Guild chat panel
- **THEN** the server persists the thread to `gnome_guild_log`, flushes draft/session snapshot, ends `gnome_guild_session`, and gnome agents become dormant

#### Scenario: Creator closes tall folk chat

- **WHEN** the Creator closes the Tall Folk chat panel
- **THEN** messages are written to `tall_folk_guild_log`, patch draft state is saved, the UI session ends, and **Tall Folk ops remain always-on**

#### Scenario: Adventurer closes Son chat

- **WHEN** an adventurer closes the Son chat dialog
- **THEN** the conversation is appended to server-side Son chat logs; the Son agent remains always-on for the next open

#### Scenario: Close with in-flight AI reply

- **WHEN** the user closes a panel while a streamed reply is incomplete
- **THEN** the server persists partial assistant content marked `truncated` or waits for stream end within a short grace timeout before flush and session end

#### Scenario: Chat via active binding

- **WHEN** a client requests chat for an entity with an active agent binding
- **THEN** the server loads the binding prompt and streams a Cursor API response

### Requirement: Creator grants life to NPCs and world items

The Creator SHALL grant agent life to manifest-defined world NPCs or world items via admin action, creating an `agent_binding` with `granted_by: creator`.

#### Scenario: Creator grants NPC life

- **WHEN** the Creator grants life to a world NPC that is otherwise static in manifest
- **THEN** an active agent binding is created and adventurers receive AI dialogue instead of static lines when interacting with that NPC

#### Scenario: Revoke or override

- **WHEN** the Creator removes or deactivates a granted binding
- **THEN** the NPC or item falls back to static behavior from manifest

### Requirement: Soul potion inventory item

The system SHALL support inventory item `soul_potion` stored per adventurer in `inventory_items`.

#### Scenario: Potion stored in inventory

- **WHEN** an adventurer receives a soul potion
- **THEN** `inventory_items.quantity` for `soul_potion` increases server-side

### Requirement: Probabilistic soul potion drop on critical success

When a dungeon run exits with ending tier **critical success**, the server SHALL roll against a configured drop probability before awarding a soul potion. The default probability SHALL be **0.35** (35%), overridable via server config (e.g. `SOUL_POTION_DROP.probability`). A drop MUST NOT occur on non-critical-success endings unless a script node explicitly grants one.

#### Scenario: Crit success with successful drop roll

- **WHEN** an adventurer completes a dungeon with critical success ending and the server drop roll succeeds
- **THEN** one soul potion is added to inventory and the exit summary shows the drop

#### Scenario: Crit success with failed drop roll

- **WHEN** an adventurer completes with critical success but the drop roll fails
- **THEN** no soul potion is awarded and the exit summary indicates no drop

#### Scenario: Non-crit success exit

- **WHEN** an adventurer exits with success but not critical success
- **THEN** the default crit-success potion drop roll is not performed

#### Scenario: Default drop probability

- **WHEN** no override is configured
- **THEN** the drop roll uses probability 0.35 (server-side uniform random in `[0, 1)`)

#### Scenario: Script node explicit grant

- **WHEN** a dungeon script node specifies an explicit soul potion grant (independent of ending tier)
- **THEN** the server awards one soul potion without requiring the crit-success drop roll

### Requirement: Soul potion misuse separate from awakening

Using soul potion on self (drink / misdrink) SHALL be a distinct action from applying to an eligible static creation. Misdrink handling SHALL be defined in `player-inventory` and logged for Truth Eye.

#### Scenario: Misdrink does not start awakening

- **WHEN** an adventurer misdrinks soul potion
- **THEN** no `awakening_session` is created

### Requirement: Creation awakening ritual

An adventurer SHALL consume one `soul_potion` to awaken an owned creation through a three-step server flow: start questions, submit answers, confirm and create binding. Each creation MAY have at most one active agent binding. Awakening via soul potion SHALL be allowed **only** for creations with `kind=object` (静物). Creations with `kind=creature` (活物) MUST NOT accept soul potion awakening.

#### Scenario: Start awakening on static object

- **WHEN** the owner calls awaken start on an owned creation with `kind=object`, at least one soul potion, and no existing binding
- **THEN** the server creates an `awakening_session` with generated questions based on creation metadata

#### Scenario: Awakening blocked for creature

- **WHEN** the owner calls awaken start on a creation with `kind=creature`
- **THEN** the server returns an error and does not create a session or consume a soul potion

#### Scenario: Start awakening blocked for wrong kind in UI

- **WHEN** the owner views a creature creation in workshop or home
- **THEN** the soul potion / awaken action is not offered for that creation

#### Scenario: Submit answers and preview

- **WHEN** the owner submits answers for a valid session
- **THEN** the server builds a draft system prompt preview from creation fields and answers

#### Scenario: Confirm awakening

- **WHEN** the owner confirms a ready session
- **THEN** the server atomically deducts one soul potion, inserts an `agent_bindings` row for the creation, and marks the session completed

#### Scenario: Awakening blocked for bound creation

- **WHEN** the creation already has an active binding
- **THEN** awaken start returns an error

### Requirement: Server-built creation prompts

Final creation agent prompts SHALL be assembled on the server from creation metadata and awakening answers. Clients MUST NOT submit authoritative system prompts.

#### Scenario: Prompt stored on binding

- **WHEN** awakening confirms
- **THEN** the resolved prompt is persisted on `agent_bindings.system_prompt` with answers snapshotted in metadata

### Requirement: Chat with awakened creation

The owner SHALL chat with an awakened creation via a dedicated chat endpoint that requires an active creation binding.

#### Scenario: Owner chats with creation agent

- **WHEN** the owner sends a message to an awakened creation at home
- **THEN** the server streams an AI reply using that creation's binding

#### Scenario: Non-owner cannot chat

- **WHEN** a non-owner attempts creation agent chat
- **THEN** the server returns 403

### Requirement: Awakening session expiry

`awakening_sessions` SHALL expire after a configured duration if not confirmed. Expired sessions MUST NOT consume soul potions.

#### Scenario: Session expires

- **WHEN** an awakening session passes expiry without confirm
- **THEN** the session status becomes expired and no potion is deducted
