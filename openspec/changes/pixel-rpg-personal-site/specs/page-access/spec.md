## ADDED Requirements

### Requirement: Page registry sync

The system SHALL register navigable pages/regions from code configuration into the `pages` table, including path, label, and optional map metadata.

#### Scenario: Application startup sync

- **WHEN** the application starts or migrations run
- **THEN** registered pages exist in the database for admin permission assignment

### Requirement: Route-level access enforcement

The system SHALL enforce UserPageAccess on protected routes via middleware and return 403 or JRPG-themed denial for unauthorized users.

#### Scenario: User lacks region access

- **WHEN** a logged-in user without access requests a protected page route
- **THEN** access is denied with a themed message

#### Scenario: User has region access

- **WHEN** a logged-in user with access requests the route
- **THEN** the page renders

### Requirement: API-level access enforcement

The system SHALL re-validate page access on sensitive API endpoints, not only hide navigation links.

#### Scenario: Direct API call without permission

- **WHEN** a user calls an API for a region they cannot access
- **THEN** the API returns 403

### Requirement: Admin routes excluded from matrix

The system SHALL NOT include `/admin/*` in UserPageAccess; admin access SHALL depend solely on `is_admin`.

#### Scenario: Admin access

- **WHEN** a user with `is_admin=true` accesses `/admin`
- **THEN** access is granted without a matrix entry
