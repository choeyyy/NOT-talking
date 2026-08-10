## ADDED Requirements

### Requirement: Sole persona agent

The system SHALL expose exactly one LLM-backed persona agent in V1: **创世主之子** (Creator's Son). All other NPCs MUST use static dialogue only and MUST NOT call the Cursor API.

#### Scenario: Static NPC remains non-agent

- **WHEN** an adventurer talks to a non-Son NPC in `/world`
- **THEN** only configured static lines are shown with no AI request

### Requirement: World maintenance role

The Creator's Son SHALL act as the world's maintainer when the Creator is unavailable, answering adventurer questions about the world and assisting with in-world matters within configured bounds.

#### Scenario: Player asks Son about the world

- **WHEN** an adventurer sends a message to the Creator's Son
- **THEN** the server proxies the message to Cursor API with the Son's system prompt and streams a reply in the Son chat UI

### Requirement: Always-available Son chat

Any logged-in adventurer SHALL be able to open a chat with the Creator's Son at any time from the sidebar or designated entry, without party or `canSee` restrictions.

#### Scenario: Player opens Son chat

- **WHEN** an adventurer clicks the Creator's Son contact
- **THEN** a dedicated chat dialog opens for messaging the Son

#### Scenario: Son chat distinct from oracle

- **WHEN** both the floating oracle and Creator's Son are available
- **THEN** they use separate UI entry points and distinct labels

### Requirement: Son may find and speak to any player

The Creator's Son SHALL bypass `canSee` for initiating and receiving direct messages with any adventurer, similar to Creator omniscience for communication.

#### Scenario: Son initiates chat with adventurer

- **WHEN** the Son maintenance flow sends a message to an adventurer
- **THEN** the message is delivered regardless of party stranger rules

#### Scenario: Adventurer replies to Son

- **WHEN** an adventurer replies in the Son chat thread
- **THEN** the reply is accepted and may trigger an AI-generated Son response

### Requirement: Son gold wallet funded by Creator

The Creator's Son SHALL have a dedicated gold balance (`son_wallet_gold`) distinct from adventurer wallets. Only the Creator MAY increase this balance via admin action.

#### Scenario: Creator funds Son wallet

- **WHEN** the Creator adds gold to the Son wallet in admin
- **THEN** `son_wallet_gold` increases and is available for Son chat grants

### Requirement: Grant gold in Son chat

The Son chat UI SHALL allow granting gold from `son_wallet_gold` to the adventurer in the active conversation, subject to server validation and Creator-configured limits per grant.

#### Scenario: Successful grant

- **WHEN** a grant of 20 gold is confirmed in Son chat and Son wallet has sufficient balance
- **THEN** 20 gold is deducted from `son_wallet_gold` and added to the adventurer's wallet gold

#### Scenario: Insufficient Son wallet

- **WHEN** a grant exceeds `son_wallet_gold`
- **THEN** the grant fails with themed feedback to request Creator funding

#### Scenario: Grant audit

- **WHEN** a grant completes
- **THEN** the transaction is persisted for Creator audit alongside chat logs

### Requirement: Son AI via Cursor API

Son replies SHALL use the server-side Cursor API proxy with a dedicated system prompt. API keys MUST NOT be exposed to clients.

#### Scenario: Streamed Son reply

- **WHEN** an adventurer message requires an AI reply from the Son
- **THEN** the server streams the response via SSE or equivalent
