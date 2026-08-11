## ADDED Requirements

### Requirement: Workshop tab for creation management

The system SHALL provide a dedicated `/workshop` tab for adventurers to create, edit, and delete owned creations independently of the home layout.

#### Scenario: Open workshop tab

- **WHEN** an adventurer navigates to `/workshop`
- **THEN** a creation management UI lists owned items with edit and delete actions

#### Scenario: Create from workshop

- **WHEN** an adventurer creates a new item from `/workshop`
- **THEN** the creation is saved and appears in both the workshop list and the home display cabinet inventory

### Requirement: Workshop hosts Gnome Guild entry (future)

When `gnome-guild` is enabled, `/workshop` SHALL include a Gnome Guild section for the Creator (see `gnome-guild` capability). The same guild is **visible** in `/world` for all adventurers, but non-Creators are **turned away at the door** with gnome refusal dialog — they do not access this workshop section.

#### Scenario: Creator sees guild on workshop

- **WHEN** the Creator opens `/workshop` and gnome guild is enabled
- **THEN** a navigation entry or panel leads to the Gnome Guild without replacing creation CRUD

#### Scenario: Adventurer has no workshop guild panel

- **WHEN** a non-Creator opens `/workshop`
- **THEN** the Gnome Guild management panel is not shown (world facade may still be visible separately)

### Requirement: Player-owned creations

The system SHALL allow adventurers to create and own personal items (`creations`) with a name, description, sprite reference, and kind (`object` for static items or `creature` for living things).

When a creation sprite is saved or updated, the server SHALL register or update a **`scope: player`** row in `art_assets` (`kind: creation_sprite`, linked to `creations.id`) per **`admin-assets`**.

#### Scenario: Create a static object

- **WHEN** an adventurer saves a new creation with kind `object`, name, description, and sprite
- **THEN** a `creations` record is stored belonging to that user

#### Scenario: Create a living creature

- **WHEN** an adventurer saves a new creation with kind `creature` and one or more phrases
- **THEN** the creation is stored with a `phrases` array for random speech

### Requirement: Edit creation description and metadata

The owner SHALL be able to update a creation's name, description, sprite, kind, and phrases (for creatures).

#### Scenario: Update description

- **WHEN** the owner edits a creation's description and saves
- **THEN** the updated description is persisted and shown on next hover or cabinet view

### Requirement: Display cabinet for creations

The home SHALL include an item display cabinet (展柜) synced with the same `creations` inventory as `/workshop`. The cabinet SHALL support drag-from-cabinet onto the home room canvas for placement.

#### Scenario: View cabinet at home

- **WHEN** an adventurer views the display cabinet on `/home`
- **THEN** owned creations are shown in a pixel-styled showcase aligned with workshop inventory

#### Scenario: Drag from cabinet to room

- **WHEN** the owner drags a creation from the home cabinet into the room canvas
- **THEN** a placement is created at the drop position and persisted in `home_config.placements`

#### Scenario: Manage cabinet entries

- **WHEN** the owner toggles cabinet visibility for a creation from home or workshop
- **THEN** the cabinet view updates in both entry points without deleting the creation record

### Requirement: Creature catchphrases

For creations with kind `creature`, the owner SHALL configure a list of short phrases the creature may say. The system SHALL support at least 1 and up to a configured maximum (e.g., 10) phrases per creature.

#### Scenario: Set creature phrases

- **WHEN** the owner saves phrases for a creature creation
- **THEN** the phrases are stored and used for random in-home speech

#### Scenario: Empty phrases for creature

- **WHEN** a creature has no phrases configured
- **THEN** it does not emit random speech bubbles

### Requirement: Soul potion not for creatures

Creations with `kind=creature` (活物) SHALL NOT be eligible for soul potion awakening (see `agent-life`). Creatures express liveness through configured `phrases` only unless the Creator grants agent life through separate admin flows (out of player potion scope).

#### Scenario: No awaken option for creature

- **WHEN** the owner manages a creature creation in `/workshop` or `/home`
- **THEN** soul potion awakening controls are hidden or disabled and API calls to awaken are rejected

#### Scenario: Object creation may awaken when potion available

- **WHEN** the owner manages an `object` creation and holds at least one soul potion
- **THEN** the UI MAY offer the awakening flow per `agent-life`

### Requirement: Sell creation at revival platform

Creations MAY be sold only through the revival-platform flow when the owner is dead and needs gold to revive. Sale requires a prior d100 appraisal in that flow and explicit owner confirmation.

#### Scenario: Sold creation removed everywhere

- **WHEN** an adventurer confirms selling a creation during revival
- **THEN** the creation record is deleted, home placements referencing it are removed, and wallet gold increases by the appraised amount

#### Scenario: Cannot sell outside revival flow when alive

- **WHEN** a living adventurer attempts to sell a creation from workshop or home
- **THEN** the system does not offer appraisal-for-sale except at the revival platform while dead

### Requirement: Creation appraisal audit trail

The system SHALL record `last_appraised_at` and `last_appraised_value` per creation to enforce the one-appraisal-per-hour rule and display the current offer when still valid.

#### Scenario: Show last appraisal in revival UI

- **WHEN** a creation was appraised 10 minutes ago and not sold
- **THEN** the revival UI shows the stored appraised value without rolling again until cooldown expires

