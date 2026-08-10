## ADDED Requirements

### Requirement: Creator admin area access

The system SHALL restrict `/admin/*` routes to users with `is_admin=true`.

#### Scenario: Non-admin accesses admin

- **WHEN** a non-admin user requests `/admin/users`
- **THEN** the system returns 403 or redirects with an access denied message

### Requirement: User CRUD by Creator

The system SHALL allow the Creator to create, list, update (including disable/enable), and delete adventurer accounts.

#### Scenario: Creator disables adventurer

- **WHEN** the Creator disables a user account
- **THEN** that user cannot log in or maintain an active session

### Requirement: Region access matrix CRUD

The system SHALL allow the Creator to grant or revoke page/region access per user via a matrix or equivalent UI bound to registered pages.

#### Scenario: Creator grants region access

- **WHEN** the Creator grants a user access to a registered page
- **THEN** that user can navigate to the corresponding route and API

### Requirement: Party assignment for social isolation

The system SHALL allow the Creator to create parties (groups) and assign each adventurer to one party. Users in different parties SHALL be treated as strangers per `social-visibility`.

#### Scenario: Creator assigns party

- **WHEN** the Creator moves a user from Party A to Party B
- **THEN** the user no longer sees members of Party A on map, chat, or gallery (except Creator omniscience)

### Requirement: Creator funds Son agent wallet

The Creator SHALL manage a dedicated `son_wallet_gold` balance used only for Creator's Son chat gold grants to adventurers.

#### Scenario: Creator tops up Son wallet

- **WHEN** the Creator adds gold to the Son wallet in admin
- **THEN** `son_wallet_gold` increases immediately

#### Scenario: View Son wallet balance

- **WHEN** the Creator opens Son agent settings in admin
- **THEN** current `son_wallet_gold` and recent grant audit entries are shown

### Requirement: Creator narrative labels

The admin UI SHALL use Creator/adventurer/region/world narrative copy consistent with the pixel TRPG theme.

#### Scenario: Admin UI display

- **WHEN** the Creator views the user management page
- **THEN** labels reflect TRPG terminology (e.g., adventurer roster, region permissions)

### Requirement: Creator chat log audit

The system SHALL provide the Creator an admin interface to browse persisted direct-message logs between adventurers and between Creator and adventurers.

#### Scenario: Creator audits conversation

- **WHEN** the Creator opens the chat log audit page and selects a conversation
- **THEN** the full message history for that thread is displayed
