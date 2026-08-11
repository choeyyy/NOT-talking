## ADDED Requirements

### Requirement: Persistent adventurer stats

Each adventurer SHALL have persistent `hp`, `max_hp`, `gold`, **`san`**, **`max_san`**, **`satiety`**, **`max_satiety`**, `attrs`, and `is_dead` stored server-side. Dungeons read and mutate wallet `hp`, `san`, and `attrs`; dungeon runs track `dungeon_exp`. **`satiety` (饱食度)** is primarily adjusted by tavern food per `world-tavern`.

#### Scenario: d100 uses attributes

- **WHEN** a check specifies a stat modifier from `attrs.str`
- **THEN** the server adjusts effective DC or tier resolution per script rules

#### Scenario: Enter dungeon with current wallet stats

- **WHEN** an adventurer starts or resumes a dungeon
- **THEN** gameplay uses current wallet `hp` and `attrs`, plus run `dungeon_exp`

#### Scenario: New adventurer stats

- **WHEN** a new adventurer account is created
- **THEN** default starting hp, max_hp, gold, and attrs are assigned per configuration

#### Scenario: Stats visible to owner

- **WHEN** an adventurer views the profile or sidebar HUD
- **THEN** current HP, gold, satiety, and attributes are displayed

### Requirement: d100 resolution rules

The system SHALL resolve d100 checks using a **shared server-side resolver** (`resolveD100(roll, effectiveDc)`). All dungeon scripts, Gnome Guild drafts, and publish validation MUST use the same tier keys and band rules documented below unless a node explicitly sets `checkProfile: "custom"` with a documented override.

**Default profile `house-coc` (跑团房规 A + CoC 分档):**

Given `roll` ∈ [1, 100] and `effectiveDc` (node DC ± stat modifiers):

| Tier key | Condition (evaluate in order; first match wins for crit bands, then success bands) |
|----------|-------------------------------------------------------------------------------------|
| `crit_failure` | `roll` ∈ [96, 100] **and** `roll > effectiveDc` |
| `crit_success` | `roll` ∈ [1, 5] **and** `roll ≤ effectiveDc` |
| `extreme_success` | `roll ≤ effectiveDc / 5` (integer floor) |
| `hard_success` | `roll ≤ effectiveDc / 2` (integer floor) |
| `success` | `roll ≤ effectiveDc` |
| `failure` | otherwise |

Tier precedence for display: `crit_success` / `crit_failure` override sub-tiers when their band rules match. If `extreme_success` or `hard_success` applies but no dedicated script outcome exists, the resolver falls back to `success`.

#### Scenario: Roll at DC 60 succeeds

- **WHEN** a check with effective DC 60 is rolled and the result is 45
- **THEN** the outcome tier is `success` and the matching script branch is applied

#### Scenario: Crit success on roll 3 at DC 60

- **WHEN** roll is 3 and effective DC is 60
- **THEN** the outcome tier is `crit_success`

#### Scenario: Crit failure on roll 98 when DC is 50

- **WHEN** roll is 98 and effective DC is 50
- **THEN** the outcome tier is `crit_failure`

#### Scenario: Hard success at DC 60

- **WHEN** roll is 28 and effective DC is 60
- **THEN** the outcome tier is `hard_success` (28 ≤ 30)

#### Scenario: Fallback when hard branch missing

- **WHEN** tier resolves to `hard_success` but the check node defines only `success` and `failure` outcomes
- **THEN** the server applies the `success` outcome

### Requirement: Standard tier keys for scripts and agents

Dungeon script check nodes and ending tiers SHALL use these canonical tier keys: `crit_success`, `extreme_success`, `hard_success`, `success`, `failure`, `crit_failure`. Gnome Guild agents MUST NOT invent alternate tier names in published JSON.

#### Scenario: Publish rejects unknown tier key

- **WHEN** a draft check node references outcome key `big_win`
- **THEN** schema validation fails at publish with a tier key error

### Requirement: Server authoritative rolls and stat changes

All d100 rolls and HP/gold mutations during dungeons SHALL occur on the server. The client MUST NOT trust client-supplied roll values for outcomes.

#### Scenario: Client requests roll

- **WHEN** the client requests advancement on a roll node
- **THEN** the server rolls 1–100, applies effects, and returns narrative and updated stats

### Requirement: Party check DC and resolution

The server SHALL implement `resolvePartyCheck()` used by dungeon check nodes when `party_size > 1`.

Given `baseDc`, per-member stat modifiers, `party_size`, and node/global `partyCheck` config:

- **`soloEffectiveDc(member)`** = `baseDc` adjusted by that member's stat modifier (unchanged house-coc resolver input).
- **`partyEffectiveDc`** = `baseDc` + chosen stat modifier + `(party_size - 1) * dcDeltaPerExtraMember` (default `dcDeltaPerExtraMember: **+5**` from `party-check-manifest` — **more members = higher DC = harder**).
- Each member rolls d100; each roll is resolved to a tier against **`partyEffectiveDc`** (not solo DC).
- **Party tier** is aggregated per `resolution` mode (`best_roll`, `worst_roll`, `majority_success`, `any_success`).
- UI payload SHALL include `baseDc`, per-member `{ roll, soloTierPreview, partyTier }`, `partyEffectiveDc`, and final `partyTier` so clients can render solo vs party lines on the **same base DC**.

#### Scenario: Two-member best_roll at base DC 60

- **WHEN** party size is 2, `baseDc` is 60, `dcDeltaPerExtraMember` is **+5**, member A rolls 48, member B rolls 63
- **THEN** `partyEffectiveDc` is **65**; A's party tier is failure, B's is success; final party tier is success under `best_roll`

#### Scenario: Solo preview uses base DC without party delta

- **WHEN** the UI renders solo preview for the same node with `baseDc` 60 and member A roll 48
- **THEN** solo preview shows **success** against effective DC 60 (+ A's stat mod only), distinct from party line against **65**
