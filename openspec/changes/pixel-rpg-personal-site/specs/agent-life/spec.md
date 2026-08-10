## ADDED Requirements

### Requirement: Agent binding as core abstraction

The system SHALL represent all persona agents (except the separate oracle tool) using `agent_bindings` records keyed by `target_type` and `target_id`. Chat SHALL route through a shared server-side Cursor API proxy using the binding's `system_prompt` and `model`.

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

### Requirement: Creation awakening ritual

An adventurer SHALL consume one `soul_potion` to awaken an owned creation through a three-step server flow: start questions, submit answers, confirm and create binding. Each creation MAY have at most one active agent binding.

#### Scenario: Start awakening

- **WHEN** the owner calls awaken start with at least one soul potion and no existing binding on the creation
- **THEN** the server creates an `awakening_session` with generated questions based on creation metadata

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
