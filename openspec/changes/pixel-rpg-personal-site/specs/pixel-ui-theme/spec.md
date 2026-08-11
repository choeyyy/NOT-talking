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

### Requirement: Mobile and desktop responsive shell

The authenticated app shell and all non-Phaser pages (login, home, workshop, profile, gallery, announcements, admin, dungeon text UI) SHALL be usable on **mobile phones** and **desktop PCs** without horizontal page scroll at default viewport widths ≥ 320 CSS px.

Layout rules:

| Breakpoint | Shell behavior |
|------------|----------------|
| **Desktop** (≥1024px) | Persistent left sidebar + main content |
| **Tablet / phone** (<1024px) | Sidebar collapses to a pixel menu control; main content uses full width |
| **Touch** | Interactive controls SHALL meet minimum ~44×44 CSS px touch targets where feasible |

Phaser `/world` SHALL scale the game canvas to fit the available viewport while preserving aspect ratio; keyboard movement on desktop; touch movement MAY defer to Phase 2 but the canvas MUST remain visible and not clip off-screen on mobile.

#### Scenario: Phone opens home tab

- **WHEN** a logged-in user opens `/home` on a 390px-wide phone browser
- **THEN** the sidebar is collapsed, room/cabinet/phone panels stack or scroll vertically, and no page-level horizontal scrollbar appears

#### Scenario: Desktop opens admin

- **WHEN** the Creator opens `/admin/users` on a 1280px desktop window
- **THEN** sidebar and CRUD table are both visible without overlapping chrome

### Requirement: Browser zoom compatibility

The UI SHALL remain functional when the user zooms the **browser page** (Ctrl/Cmd +, pinch zoom on mobile) up to **200%** relative to default:

- Text and controls remain readable and not permanently clipped
- Primary actions remain reachable without horizontal scroll on shell pages
- Fixed-position widgets (oracle, chat) reflow or shrink so they do not cover the entire viewport at 200% zoom

Implementation guidance (non-normative): use relative units (`rem`, `%`, `clamp`) for typography and spacing; avoid hard-coded viewport widths for main layout; test at 100% and 200% browser zoom.

#### Scenario: User zooms to 200% on login

- **WHEN** a user sets browser zoom to 200% on `/login`
- **THEN** the login form and title remain visible and submittable without sideways scrolling

#### Scenario: User zooms during dungeon text play

- **WHEN** a user reads dungeon narrative at 150% browser zoom
- **THEN** choice buttons wrap or scroll within the panel without breaking layout

### Requirement: Mobile dark theme

On **mobile user agents** (phone/tablet form factors), the app SHALL present a **dark theme** by default: dark backgrounds, light primary text, sufficient contrast for body copy and buttons (target WCAG AA for normal text where practical).

The theme SHALL also respect **`prefers-color-scheme: dark`** when the OS reports dark mode; light mode on mobile MAY be unsupported in V1 if all tokens are dark-first.

Dark tokens SHALL apply consistently to: shell sidebar, dialogs, forms, home phone UI, dungeon text panels, and floating oracle/chat chrome. Pure-white full-screen flashes on route change MUST NOT occur on mobile.

#### Scenario: iPhone dark mode

- **WHEN** an adventurer opens the site on iPhone with system dark appearance enabled
- **THEN** pages render with dark background and light text without an unintended light flash on first paint

#### Scenario: Mobile oracle panel

- **WHEN** the user opens the AI oracle on a phone
- **THEN** the panel uses dark-theme tokens and remains readable outdoors at default brightness
