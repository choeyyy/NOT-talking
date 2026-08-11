## Status

**DISCUSSION** — 2026-08-11 用户提案「防止 Agent 抽风」；适用于之子、神谕、地精、长身人及赋活造物 Agent。见 `discussion-log.md` §O。

## ADDED Requirements

### Requirement: Single AgentRouter gateway

All LLM persona traffic (Son, oracle, gnomes, tall folk, awakened creations) MUST pass through one server-side **`AgentRouter`**. Agents MUST NOT call Cursor API directly from client code, background jobs without routing, or with user-supplied system prompts.

The router SHALL enforce: authentication, agent binding lookup, rate limits, output caps, tool allowlists, and audit logging **before** and **after** each model call.

#### Scenario: Client cannot set system prompt

- **WHEN** a client POST includes a `systemPrompt` field for Son or oracle chat
- **THEN** the server ignores or rejects it and uses only the server-assembled prompt from `agent_bindings`

#### Scenario: Unknown agent id rejected

- **WHEN** a request references an agent binding the caller is not allowed to use
- **THEN** the router returns 403 without calling Cursor API

### Requirement: Tool and side-effect allowlist

Agents MUST NOT receive open-ended tools (shell, SQL, filesystem, arbitrary HTTP). The server SHALL expose **only** named, schema-validated actions per agent class:

| Agent class | Allowed server actions (examples) |
|-------------|-----------------------------------|
| **Son** | `son_chat_reply`, `son_grant_gold` (within limits) |
| **Oracle** | `oracle_chat_reply` only — **no** wallet, publish, or admin mutations |
| **Gnomes** | `guild_chat_reply`, `upsert_dungeon_draft`, `propose_publish` — **not** `execute_publish` |
| **Tall folk** | `guild_chat_reply`, `upsert_runtime_patch_draft`, `propose_deploy` — **not** `execute_deploy` |
| **Awakened creation** | `creation_chat_reply` only |

Any model output that requests a disallowed action MUST be discarded; the router MAY return a safe fallback line to the user.

#### Scenario: Gnome attempts direct publish in tool call

- **WHEN** model output includes `execute_publish` without a recorded Creator approval token
- **THEN** the action is blocked and the draft status remains unchanged

#### Scenario: Oracle requests gold grant

- **WHEN** oracle model output includes a wallet mutation tool
- **THEN** the router rejects the tool call and streams a narrative-only reply

### Requirement: Human approval for irreversible world changes

The following MUST require **explicit Creator confirmation** on a server endpoint separate from free-form chat (button, signed approve token, or structured confirm command parsed with idempotency):

- Gnome **publish** → `dungeon_scripts` / entrances / announcements
- Tall folk **T0 patch apply**, **T1 worker reload**, **T2 deploy**
- Admin studio **scene publish** (per `admin-studio`)
- Son **gold grant** above per-transaction limit (optional second confirm)

Agents MAY **propose** changes in chat; they MUST NOT apply irreversible changes from chat text alone without the confirm endpoint succeeding.

#### Scenario: Chat-only approval insufficient

- **WHEN** the Creator types 「批准发布」 in guild chat but does not trigger the publish confirm action
- **THEN** `dungeon_scripts` is not updated until the structured confirm API succeeds

### Requirement: Schema validation before persisting agent artifacts

| Artifact | Validation |
|----------|------------|
| `dungeon_script_drafts` | `dungeons` JSON schema + `house-coc` tier keys |
| `runtime_patch_drafts` (T0) | Patch schema + allowed keys whitelist |
| T2 deploy bundles | Lint/test gate in CI; no auto-merge |

Invalid model-generated JSON MUST NOT be saved as `published` or applied to live tables; errors SHALL be surfaced to the Creator in guild UI.

#### Scenario: Engine gnome outputs invalid tier key

- **WHEN** draft JSON contains a non-canonical outcome key
- **THEN** upsert to draft may save as `drafting` with validation errors, but publish API returns 400

### Requirement: Rate limits and session budgets

The server SHALL enforce configurable rate limits:

| Scope | Default policy (overridable) |
|-------|------------------------------|
| Per adventurer Son chat | e.g. 30 messages / hour |
| Per user oracle | e.g. 20 messages / hour |
| Per Creator **gnome** guild session | e.g. 60 gnome turns / session |
| Tall Folk **background ops** | e.g. 1 scheduled diagnostic / 15 min; cap daily Cursor calls |
| Per Creator **tall-folk** chat session | e.g. 60 tall-folk turns / session |
| Global Cursor API | circuit breaker on error rate |

When limits are exceeded, the server SHALL return themed feedback and MUST NOT call Cursor API until the window resets.

The Creator SHOULD configure **daily or global token/call budgets** in `/admin/agents` (implementation detail; see `discussion-log.md` §S). When budget is exhausted, agents return themed maintenance/busy messages without model calls.

#### Scenario: Son spam blocked

- **WHEN** an adventurer exceeds the Son hourly message cap
- **THEN** further messages receive a cooldown response without an AI call

### Requirement: Output length and scope caps

| Context | Cap |
|---------|-----|
| Gnome adventurer **refusal** | Short dialog; refusal-only prompt; static fallback |
| Tall Folk adventurer **refusal** | **Static only** — canonical **「非法闯入请刷卡。」**; no Cursor API |
| Son player chat | Max tokens per reply; no admin spoilers in prompt context |
| Oracle | Narrative/hint only; no live DB dumps of other users |
| Guild draft JSON | Max script size / node count server-side |

Prompts SHALL instruct agents to stay in character and refuse out-of-scope requests (delete users, reveal secrets, disable login wall, etc.).

#### Scenario: Son asked to reveal another player's password

- **WHEN** an adventurer prompts the Son for credentials or admin secrets
- **THEN** the Son refuses in character and no sensitive data is included in the model context

### Requirement: Creator kill switch

The Creator admin SHALL have toggles to **disable all agents** or **disable per agent class** (Son, oracle, gnomes, tall folk, awakened creations). When disabled, endpoints return themed maintenance messages and Cursor API is not called.

#### Scenario: Creator disables gnomes during incident

- **WHEN** the Creator sets `gnome_agents_enabled=false`
- **THEN** guild chat cannot invoke gnome models until re-enabled; published dungeons remain playable from DB

### Requirement: Circuit breaker and static fallback

When Cursor API fails, times out, or returns policy violations, the router SHALL:

1. Log the failure with agent id and request id
2. Increment error metrics
3. Return **static or cached safe fallback** where defined (gnome refusal pools, generic Son busy line)
4. Open circuit temporarily after repeated failures to protect cost and UX

#### Scenario: API outage during gnome refusal

- **WHEN** Cursor API is unavailable for a world entrance refusal
- **THEN** a random static line from manifest is shown (including canonical 「让我来看看是谁没被邀请。」)

### Requirement: Audit log for agent side effects

Every successful **side-effect action** (grant gold, draft upsert, publish, patch apply, deploy approve) SHALL write to Creator-auditable logs with: actor user id, agent binding id, action name, target id, before/after snapshot reference, timestamp, and whether AI or manual.

Chat text alone without a side-effect action MAY be logged per existing chat log policy.

#### Scenario: Publish audited

- **WHEN** a dungeon draft is published after Creator confirm
- **THEN** audit log records draft id, version, and `script_version` applied

### Requirement: Son and player-facing agents cannot escalate privilege

The Son and awakened creation agents MUST NOT:

- Publish dungeons or patches
- Modify `UserPageAccess`, party, or acquaintance tables
- Grant items other than configured gold grants from `son_wallet_gold`
- Wake dormant **gnome** guild agents
- Expose other users' private logs, wallets beyond public game rules, or admin routes

#### Scenario: Son asked to publish dungeon

- **WHEN** the Son chat receives a request to publish a gnome draft
- **THEN** the Son refuses and no publish API is invoked
