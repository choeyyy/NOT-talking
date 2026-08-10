## ADDED Requirements

### Requirement: Adventurer display name self-service

The system SHALL allow authenticated users to update their own `display_name`. Users SHALL NOT update other users' names via self-service endpoints.

#### Scenario: User updates name

- **WHEN** a user submits a valid display name on the character profile page
- **THEN** the name is saved and shown across the site for users who can see them

### Requirement: Layered character customization

The system SHALL provide layered pixel character customization (e.g., body, hair, clothing, colors) and store selections in `character_config` JSON.

#### Scenario: User saves character

- **WHEN** a user saves customization choices
- **THEN** `character_config` is persisted and a composed avatar image is generated

### Requirement: Character card presentation

The profile UI SHALL present customization as a JRPG-style character card with preview.

#### Scenario: Profile page load

- **WHEN** a user opens the character profile tab
- **THEN** the current sprite preview and customization controls are displayed

### Requirement: Avatar used in map and gallery

The composed avatar SHALL be the visual representation on the world map (when online) and in the gallery (when opted in).

#### Scenario: Avatar composition

- **WHEN** character config changes
- **THEN** the updated sprite is used for subsequent map and gallery renders
