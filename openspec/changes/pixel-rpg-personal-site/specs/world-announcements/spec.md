## ADDED Requirements

### Requirement: Creator announcement CRUD

The system SHALL allow the Creator to create, read, update, and delete world announcements with fields including title, body, published state, pinned flag, and optional expiry.

#### Scenario: Creator publishes announcement

- **WHEN** the Creator publishes an announcement
- **THEN** it becomes visible to all logged-in adventurers

### Requirement: Logged-in users read announcements

The system SHALL display published non-expired announcements to all authenticated users via a site banner and/or `/announcements` list.

#### Scenario: Adventurer views announcements

- **WHEN** a logged-in user visits `/announcements`
- **THEN** published announcements are listed in reverse chronological order with pinned items first

#### Scenario: Unauthenticated user cannot read announcements

- **WHEN** an unauthenticated user requests announcement APIs or pages
- **THEN** access is denied by the login wall
