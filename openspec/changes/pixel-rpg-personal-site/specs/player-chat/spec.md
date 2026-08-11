## ADDED Requirements

### Requirement: Mutual chat between acquaintances

The system SHALL allow two adventurers to send direct messages to each other when they are mutual acquaintances: `canSee(A,B)` and `canSee(B,A)` are both true (via same party, mutual `user_acquaintances` from tavern ritual, or Creator admin link).

#### Scenario: Acquaintances exchange messages

- **WHEN** adventurer A sends a message to adventurer B and both can see each other
- **THEN** the message is stored and delivered to B if online

#### Scenario: Acquaintance initiates chat from map

- **WHEN** an adventurer clicks the sprite of a visible acquaintance on `/world`
- **THEN** a chat dialog opens and the adventurer may send live messages

#### Scenario: Strangers cannot message

- **WHEN** user A attempts to message user B and `canSee(A,B)` is false
- **THEN** the system returns 403 with a themed error

### Requirement: Tavern table ephemeral chat

Tavern **same-table** chat SHALL be governed by `world-tavern`, not this requirement. Table chat bypasses stranger DM restrictions while seated but MUST NOT use the `messages` table or persistent DM APIs documented below.

#### Scenario: Tavern table chat not in messages table

- **WHEN** strangers exchange messages at the same tavern table
- **THEN** those lines are delivered via the tavern table channel only and are not persisted as direct messages

#### Scenario: Post-tavern persistent DM still blocked

- **WHEN** two strangers chatted at a tavern table and later one attempts persistent DM outside the table
- **THEN** the persistent message API applies `canSee` and rejects if false

### Requirement: Creator's Son chat bypass

The Creator's Son agent SHALL bypass `canSee` for direct messages with any adventurer. Adventurers SHALL always be able to open a chat with the Son without stranger restrictions.

#### Scenario: Stranger messaged by Son

- **WHEN** the Son sends a message to an adventurer in a different party
- **THEN** the message is delivered and the adventurer may reply

#### Scenario: Player opens Son chat anytime

- **WHEN** any logged-in adventurer opens the Creator's Son contact
- **THEN** a chat dialog is available regardless of party

#### Scenario: Creator messages stranger party member

- **WHEN** the Creator sends a message to an online adventurer in a different party
- **THEN** the message is stored and delivered if online

#### Scenario: Creator messages from omniscience list

- **WHEN** the Creator selects any adventurer from the global online list
- **THEN** the Creator can open chat and send messages to that adventurer

#### Scenario: Adventurer replies to Creator

- **WHEN** an adventurer receives a live message from the Creator in an open chat dialog
- **THEN** the adventurer may reply in real time even if they would not otherwise initiate cross-party contact

### Requirement: Creator's Son chat bypass and gold grants

The Creator's Son agent SHALL bypass `canSee` for messaging any adventurer. Any adventurer SHALL open Son chat at any time. Son chat MAY grant gold from `son_wallet_gold` to the adventurer per `creator-son-agent` rules.

#### Scenario: Player opens Son chat anytime

- **WHEN** any logged-in adventurer opens the Creator's Son contact from sidebar or world interactable
- **THEN** the Son chat dialog opens regardless of party

#### Scenario: Son finds and messages player

- **WHEN** the Son maintenance flow sends a message to an adventurer
- **THEN** delivery succeeds regardless of stranger rules and may trigger AI reply generation

#### Scenario: Gold grant in Son chat

- **WHEN** a gold grant is confirmed in Son chat with sufficient `son_wallet_gold`
- **THEN** adventurer wallet gold increases and Son wallet decreases

### Requirement: Chat available outside world tab

The system SHALL allow sending and receiving direct messages on any authenticated tab, not only on `/world`.

#### Scenario: Receive message on announcements tab

- **WHEN** a user receives a DM while on `/announcements`
- **THEN** a chat notification or panel can display the message

### Requirement: Open chat from map interaction

The system SHALL allow the Creator to open a chat dialog from the global online list or by clicking any adventurer sprite visible to the Creator on `/world`. Adventurers SHALL open chat only by clicking sprites of acquaintances they can see on the map.

#### Scenario: Creator clicks any online adventurer

- **WHEN** the Creator clicks an adventurer in the omniscience list or on the map
- **THEN** a chat dialog opens with that adventurer

#### Scenario: Adventurer clicks acquaintance sprite

- **WHEN** an adventurer clicks another adventurer's sprite that is visible per `canSee`
- **THEN** a chat dialog opens between the two acquaintances

### Requirement: Phone chat from home

Adventurers on `/home` SHALL open live chat with online mutual acquaintances via the phone interaction without requiring presence on `/world`.

#### Scenario: Chat from home phone

- **WHEN** an adventurer at home selects an online acquaintance from the phone list
- **THEN** live messages may be sent and received per `canSend()` rules

### Requirement: Message persistence for audit

The system SHALL persist all **direct messages** (persistent DM and Creator/Son threads) with sender, recipient, body, and timestamp in the database for audit purposes. **Tavern table chat** per `world-tavern` is excluded and MUST NOT be written to this table.

#### Scenario: Message stored on send

- **WHEN** a permitted user sends a direct message
- **THEN** the message is written to the database regardless of recipient online status

### Requirement: Chat logs Creator-only

The system SHALL restrict conversation history retrieval to users with `is_admin=true`. Adventurers MUST NOT access historical chat logs via API or UI.

#### Scenario: Adventurer cannot load history

- **WHEN** a non-admin user requests conversation history for any pair of users
- **THEN** the system returns 403

#### Scenario: Creator loads conversation history

- **WHEN** the Creator requests conversation history for two adventurers or a Creator-adventurer thread
- **THEN** the system returns the full persisted log ordered by timestamp

### Requirement: Adventurer ephemeral chat view

Adventurers SHALL receive and display direct messages in real time only while a chat session is open. The client MUST NOT persist or reload historical messages for non-admin users after refresh or navigation.

#### Scenario: Adventurer receives live message

- **WHEN** an adventurer has an open chat dialog and a new message arrives via WebSocket
- **THEN** the message appears in the dialog but is not reloadable as history after the session ends

#### Scenario: Adventurer reopens chat

- **WHEN** a non-admin user reopens a chat dialog after closing or refreshing
- **THEN** no prior messages are loaded; only new live messages appear
