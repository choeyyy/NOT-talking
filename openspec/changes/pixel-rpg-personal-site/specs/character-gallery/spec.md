## ADDED Requirements

### Requirement: Gallery tab for character exhibition

The system SHALL provide `/gallery` displaying a grid of adventurer portraits and display names for eligible entries.

#### Scenario: User browses gallery

- **WHEN** a logged-in user opens `/gallery`
- **THEN** visible character entries are shown in a grid layout

### Requirement: Opt-in gallery visibility

The system SHALL include a `gallery_visible` flag on user profiles defaulting to false. Only users with `gallery_visible=true` and a saved character SHALL appear in the gallery.

#### Scenario: User opts in

- **WHEN** a user enables gallery visibility and saves a character
- **THEN** their entry appears in the gallery for users who can see them

#### Scenario: User opts out

- **WHEN** a user disables gallery visibility
- **THEN** their entry is removed from the gallery list

### Requirement: Gallery filtered by canSee

The gallery list SHALL filter entries using `canSee(viewer, owner)`. Strangers MUST NOT appear in each other's gallery results.

#### Scenario: Cross-party strangers

- **WHEN** users in different parties browse the gallery
- **THEN** they do not see each other's entries

#### Scenario: Creator omniscience in gallery

- **WHEN** the Creator browses the gallery
- **THEN** all opted-in characters are visible

### Requirement: Character detail view

The system SHALL allow clicking a gallery entry to view a larger portrait and display name in a JRPG-style detail card.

#### Scenario: Open detail card

- **WHEN** a user clicks a gallery tile they can see
- **THEN** a detail view with enlarged sprite and name is shown
