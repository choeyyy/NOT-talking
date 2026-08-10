## ADDED Requirements

### Requirement: Floating oracle for logged-in users

The system SHALL provide a global floating AI widget available on all authenticated pages.

#### Scenario: Logged-in user opens oracle

- **WHEN** an authenticated user clicks the floating oracle control
- **THEN** a chat panel opens without leaving the current page

#### Scenario: Unauthenticated user has no oracle

- **WHEN** an unauthenticated user is on `/login`
- **THEN** the AI oracle widget is not available

### Requirement: Dual model selection

The system SHALL allow selecting between `composer-2.5` and `grok-4.5` models for each conversation turn.

#### Scenario: Model switch

- **WHEN** a user selects Grok 4.5 and sends a message
- **THEN** the request is proxied with the Grok model mapping

### Requirement: Server-side Cursor API proxy

The system SHALL proxy AI requests to Cursor API on the server using `CURSOR_API_KEY`. The API key MUST NOT be exposed to the client.

#### Scenario: Chat streaming

- **WHEN** a user sends a message via the oracle
- **THEN** the server streams the model response via SSE or equivalent to the client

### Requirement: Oracle distinct from player chat

The AI oracle UI SHALL be visually and functionally distinct from adventurer-to-adventurer chat.

#### Scenario: Both widgets available

- **WHEN** a logged-in user is on any page
- **THEN** oracle and player chat entry points are distinguishable

### Requirement: Oracle distinct from Creator's Son

The oracle MUST NOT grant gold or use the Son persona. Creator's Son chat uses a separate API route and UI.

#### Scenario: Oracle is not Son

- **WHEN** an adventurer opens the floating oracle
- **THEN** the interface is labeled as oracle/shrine tool, not Creator's Son
