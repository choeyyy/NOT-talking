## ADDED Requirements

### Requirement: Login wall blocks unauthenticated access

The system SHALL redirect unauthenticated users to `/login` for all routes except `/login`, `/api/auth/*`, and static assets.

#### Scenario: Unauthenticated user visits protected route

- **WHEN** an unauthenticated user requests `/dashboard`
- **THEN** the system redirects to `/login`

#### Scenario: Authenticated user accesses protected route

- **WHEN** an authenticated user requests a route they are permitted to access
- **THEN** the system allows the request

### Requirement: Admin creates user accounts

The system SHALL allow users with `is_admin` to create accounts with email and initial password. Self-registration SHALL NOT be available in V1.

#### Scenario: Creator creates adventurer

- **WHEN** the Creator submits valid email and password on the admin users form
- **THEN** a new user record is created and can log in

### Requirement: Session-based authentication

The system SHALL authenticate users via email and password and maintain session via httpOnly secure cookie.

#### Scenario: Successful login

- **WHEN** a user submits valid credentials on `/login`
- **THEN** the system establishes a session and redirects to the default landing page

#### Scenario: Failed login

- **WHEN** a user submits invalid credentials
- **THEN** the system rejects login with an error and does not create a session

### Requirement: Initial Creator seed

The system SHALL provide a seed mechanism to create the first `is_admin` user for deployment.

#### Scenario: First deploy

- **WHEN** no admin exists and seed script runs with configured credentials
- **THEN** one Creator account with `is_admin=true` exists
