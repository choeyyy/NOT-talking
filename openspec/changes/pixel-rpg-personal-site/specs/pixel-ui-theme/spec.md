## ADDED Requirements

### Requirement: Sidebar primary navigation

The authenticated app shell SHALL use a **left sidebar** for primary route navigation (home, workshop, world, dungeon, gallery, announcements, profile, admin). A horizontal top navigation bar MUST NOT be used for primary routes.

#### Scenario: Sidebar shows main routes

- **WHEN** a logged-in user views any protected page
- **THEN** a persistent left sidebar lists available routes with pixel JRPG styling

#### Scenario: No top primary nav bar

- **WHEN** a logged-in user views the protected layout
- **THEN** primary route links are not rendered in a horizontal top tab bar

#### Scenario: Main content area

- **WHEN** the user selects a sidebar route
- **THEN** the selected page renders in the main content area to the right of the sidebar

#### Scenario: Sidebar respects page access

- **WHEN** a user lacks access to a registered page
- **THEN** that route is hidden or disabled in the sidebar per UserPageAccess rules

### Requirement: Pixel JRPG visual theme

The system SHALL apply a cohesive pixel TRPG visual theme across authenticated pages including pixel-friendly fonts, chunky borders, and JRPG dialog components.

#### Scenario: Login title screen

- **WHEN** a user visits `/login`
- **THEN** the page presents a title-screen-style pixel layout

### Requirement: Themed access denial dialogs

Access denial states (403 region locked, stranger blocked) SHALL use JRPG dialog styling and TRPG narrative copy.

#### Scenario: Region locked

- **WHEN** a user attempts to enter a locked map building
- **THEN** a pixel-styled dialog explains the region is not yet granted

### Requirement: Creator admin theming

Admin pages SHALL use Creator altar / celestial console theming while maintaining usable information density for CRUD tasks.

#### Scenario: Admin users page

- **WHEN** the Creator opens user management
- **THEN** TRPG-themed labels and pixel framing are applied to forms and tables

### Requirement: Pixelated avatar rendering

Character avatars SHALL render with pixelated scaling (`image-rendering: pixelated` or equivalent) where enlarged.

#### Scenario: Gallery enlarged portrait

- **WHEN** a portrait is displayed larger than native sprite size
- **THEN** scaling preserves crisp pixel edges

### Requirement: Separate visual identity for oracle and chat

The AI oracle and adventurer chat widgets SHALL have distinct pixel-themed icons and panel chrome to avoid user confusion.

#### Scenario: Widget distinction

- **WHEN** both widgets are available
- **THEN** their icons and panel headers are visually distinct
