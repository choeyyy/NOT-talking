## 1. Project Setup

- [ ] 1.1 Initialize Next.js App Router project with TypeScript, Tailwind, ESLint
- [ ] 1.2 Add shadcn/ui and configure pixel JRPG theme tokens (fonts, colors, borders)
- [ ] 1.3 Set up Drizzle ORM with SQLite and migration tooling
- [ ] 1.4 Create `.env.example` with `DATABASE_URL`, `SESSION_SECRET`, `CURSOR_API_KEY`, `MODEL_MAP`
- [ ] 1.5 Add Dockerfile and docker-compose for app + volumes (db, uploads)

## 2. Database Schema

- [ ] 2.1 Create `users` table (…, hp, max_hp, gold, satiety, max_satiety, attrs JSON, is_dead, character_config, home_config, …)
- [ ] 2.2 Create `pages` table and `user_page_access` junction table
- [ ] 2.3 Create `parties` and `user_parties` tables for social visibility
- [ ] 2.4 Create `announcements` table (title, body, is_published, pinned, expires_at)
- [ ] 2.5 Create `messages` table for DM persistence
- [ ] 2.6 Create `creations` table (…, last_appraised_at, last_appraised_value)
- [ ] 2.7 Create `dungeon_runs` table (…, `script_version` pinned at run start)
- [ ] 2.7a Create `dungeon_scripts` (id, label, script_json, version, is_published, published_at, source_draft_id)
- [ ] 2.7b Create `dungeon_entrances` (scene_id, position, dungeon_id, label, is_active) — runtime entrances, merge with Tiled
- [ ] 2.7c Create `dungeon_run_log`, `dungeon_ui_log` tables (archivist telemetry)
- [ ] 2.7d Create `dungeon_script_drafts`, `gnome_guild_log` (gnome-guild; can defer migration to Phase 23)
- [ ] 2.8 Create `son_wallet` or settings row for `son_wallet_gold` + grant audit table
- [ ] 2.9 Create `inventory_items`, `agent_bindings`, `awakening_sessions` tables
- [ ] 2.10 Implement admin seed script for first Creator account

## 3. Auth & Login Wall (auth-session)

- [ ] 3.1 Implement credentials auth with bcrypt and httpOnly session
- [ ] 3.2 Build pixel-themed `/login` title screen page
- [ ] 3.3 Add middleware login wall (whitelist `/login`, `/api/auth/*`, static assets)
- [ ] 3.4 Add session helpers and protected layout wrapper
- [ ] 3.5 Redirect successful login to `/home` by default

## 4. Page Registry & Access (page-access)

- [ ] 4.1 Create `site-pages.ts` registry with paths, labels, map metadata
- [ ] 4.2 Implement startup sync from registry to `pages` table
- [ ] 4.3 Add middleware/route guards for UserPageAccess with JRPG 403 page
- [ ] 4.4 Add API middleware helper to validate page access on sensitive routes

## 5. Creator Admin (admin-creator)

- [ ] 5.1 Build `/admin` hub sidebar: 神视、用户、区域、公告、studio、scenes、logs、son、gnome-guild、玩家页预览
- [ ] 5.2 Implement user CRUD API and adventurer roster UI
- [ ] 5.3 Implement region permission matrix UI and API
- [ ] 5.4 Implement party CRUD, acquaintance override, user party assignment UI
- [ ] 5.5 Embed pixel studio at `/admin/studio`（apply 时新做 UI；spec: `admin-studio` §K）
- [ ] 5.5a **`POST /api/admin/studio/recognize`** + **`/place`** + staging
- [ ] 5.5b Scene publish → `public/assets` + manifest; audit log
- [ ] 5.6 `/admin/scenes` manifest + dungeon_entrances + import studio JSON
- [ ] 5.7 `/admin/chat-logs` + `/admin/behavior-logs` (+ dungeon log summary)
- [ ] 5.8 `/admin/son` wallet, grant audit, settings
- [ ] 5.9 `/admin/gnome-guild` link (shared guild UI with workshop)
- [ ] 5.10 **`/admin/dungeons`** — Creator edit drafts + published `script_json`; T0 publish/hotfix (no gnome required)
- [ ] 5.11 **`/admin/assets`** — `art_assets` registry; global + player; catalog number, metadata edit, optional PNG replace

## 5b. Admin Asset Library (admin-assets)

- [ ] 5b.1 Create `art_assets` table (scope, owner, kind, asset_number, storage_url, metadata, version)
- [ ] 5b.2 Build `/admin/assets` UI: filter global/player, search by number/tag, edit details
- [ ] 5b.3 On player save profile/workshop sprite → upsert player-scoped `art_assets` row
- [ ] 5b.4 Wire `/admin/npcs` sprite picker to `art_asset_id`; T0 cache invalidate on update
- [ ] 5.10 Preview links to all adventurer routes as Creator
- [ ] 5.11 Apply TRPG copy to all admin labels and actions

## 6. Social Visibility (social-visibility)

- [ ] 6.1 Implement `canSee(viewer, target)` — same party OR mutual `user_acquaintances`; Creator bypass
- [ ] 6.2 Assign new users to **solo default party** on creation (stranger-by-default)
- [ ] 6.3 Unit-test canSee for same-party, cross-party, tavern-acquaintance, and Creator cases
- [ ] 6.4 `user_acquaintances` table + Creator admin CRUD override

## 7. Character Profile & Customization (character-profile)

- [ ] 7.1 Build `/profile` character card page with display name editing
- [ ] 7.2 Integrate LPC-style layered customization UI and `character_config` storage
- [ ] 7.3 Implement Canvas avatar composition and save to `avatar_url`/uploads
- [ ] 7.4 Add gallery_visible opt-in toggle on profile page

## 8. World Announcements (world-announcements)

- [ ] 8.1 Implement announcements CRUD API (admin only)
- [ ] 8.2 Build `/admin/announcements` management UI
- [ ] 8.3 Add site-wide announcement banner in protected layout
- [ ] 8.4 Build `/announcements` list page for logged-in users

## 9. Pixel UI Theme (pixel-ui-theme)

- [ ] 9.1 Create reusable JRPG dialog, button, panel, and tab components
- [ ] 9.2 Build protected app shell with **left sidebar** nav (家, 造物, 世界, 副本, 展馆, 公告, 角色…); no top tab bar
- [ ] 9.3 Ensure avatars use pixelated rendering when scaled
- [ ] 9.4 Style access-denial and error states with TRPG copy
- [ ] 9.5 Responsive shell: collapsible sidebar `<1024px`, touch targets, no horizontal scroll ≥320px
- [ ] 9.6 Browser zoom 100%–200%: rem/clamp layout, floating widgets reflow
- [ ] 9.7 Mobile dark theme tokens + `prefers-color-scheme: dark`; no light flash on first paint
- [ ] 9.8 Document viewport meta + manual QA checklist (iPhone Safari, Android Chrome, desktop 1280/200% zoom)

## 10. AI Oracle (ai-oracle)

- [ ] 10.1 Implement `POST /api/ai/chat` SSE proxy to Cursor API with model map
- [ ] 10.2 Build floating oracle widget in root layout (logged-in only)
- [ ] 10.3 Add model selector (composer-2.5, grok-4.5) and streaming UI
- [ ] 10.4 Add basic per-user rate limiting for AI requests

## 10b. Agent Safety (agent-safety)

- [ ] 10b.1 Implement `AgentRouter`: binding lookup, rate limits, output caps, audit hook
- [ ] 10b.2 Tool allowlist per agent class; block disallowed model tool calls
- [ ] 10b.3 Structured confirm endpoints for publish / patch / deploy (chat-only approval insufficient)
- [ ] 10b.4 Creator kill switches in `/admin` per agent class + global
- [ ] 10b.5 Circuit breaker + static fallbacks (gnome refusal, Son busy line)
- [ ] 10b.6 Schema validation gate on draft upsert and publish
- [ ] 10b.7 Chat panel `session/close`: persist logs, flush draft snapshot; **gnome** → dormant; **Son + Tall Folk ops** → UI session only

## 11. Player Creations (player-creations) — Phase 1.5a

- [ ] 11.1 Implement creations CRUD API (owner only)
- [ ] 11.2 Build `/workshop` tab: creation list, create/edit form (name, description, kind, sprite, phrases)
- [ ] 11.3 Sync workshop inventory with home display cabinet data model
- [ ] 11.4 Validate phrases max count and description length server-side

## 12. Home Tab (home-space) — Phase 1.5a

- [ ] 12.1 Build `/home` pixel room with cabinet panel, placement canvas, and phone
- [ ] 12.2 Implement drag-from-cabinet to room canvas; persist `home_config.placements`
- [ ] 12.3 Add shortcut link from home cabinet to `/workshop`
- [ ] 12.4 Hover tooltip showing creation description
- [ ] 12.5 Creature random speech bubbles from `phrases` while owner views home
- [ ] 12.6 Online acquaintances API + phone chat flow
- [ ] 12.7 Register home presence context `home`

## 13. World Map Tab (world-map) — Phase 1.5b

- [ ] 13.1 Add `world-scene-manifest.ts` with initial scene pack
- [ ] 13.2 Add Phaser 3 dynamic import on `/world` only
- [ ] 13.3 Implement scene_door, portal_door, dungeon_entrance handlers
- [ ] 13.4 Tiled assets for hub-plaza, garden-view, tavern-hall, shrine-outer, portrait-hall
- [ ] 13.5 Player movement, collision, sprite; portal to `/gallery`

## 14. World NPCs (world-npcs) — Phase 1.5c

- [ ] 14.1 Bootstrap `world_npcs` from seed; runtime load + cache invalidate on admin save
- [ ] 14.1b **`/admin/npcs`** — dialogue + **player address** fields; T0 hot update
- [ ] 14.1c Optional WS `world_npcs_updated` for in-scene live refresh
- [ ] 14.2 Seed **`li_luang`** (Li-Luang; player address seed **乖孙**; dialogue theme AA — content via admin)
- [ ] 14.3 Build JRPG static dialogue UI for generic NPCs
- [ ] 14.4 Add Creator's Son interactable in hub-plaza opening Son chat

## 14b. Creator's Son Agent (creator-son-agent) — Phase 1.5c

- [ ] 14b.1 Implement `POST /api/son/chat` with Son system prompt + Cursor SSE
- [ ] 14b.2 Son sidebar contact always visible; bypass canSee for Son threads
- [ ] 14b.3 Son online list / find-player to initiate chat (Creator-off duty maintenance)
- [ ] 14b.4 `son_wallet_gold` + admin top-up + `POST /api/son/grant-gold` in chat UI
- [ ] 14b.5 Persist Son chat + grant audit; log visible to Creator only
- [ ] 14b.6 Distinguish Son chat UI from oracle widget and adventurer chat

## 15. Dungeons & TRPG (dungeons + trpg-mechanics) — Phase 1.5c

- [ ] 15.1 Seed sample dungeon JSON into `dungeon_scripts` via migration (bootstrap only; not the gnome publish path)
- [ ] 15.2 Build `/dungeon/[id]` JRPG log UI (text, choices, roll button)
- [ ] 15.2a Implement `DungeonScriptLoader` (DB load + short TTL cache + invalidate on publish)
- [ ] 15.3 Implement `d100-resolver.ts` with `house-coc` profile + tier fallback; wire to script-schema tier keys
- [ ] 15.4 Apply wallet hp/attrs immediately; track dungeon_exp and run flags
- [ ] 15.5 Implement ending resolver (conditions on exp, attrs, flags)
- [ ] 15.6 Death flow: is_dead, redirect to world revival spawn, block re-entry
- [ ] 15.7 Persist dungeon_runs with `script_version` pinned at start; merge run_gold on successful exit
- [ ] 15.8 Persist `dungeon_run_log` and `dungeon_ui_log` per dungeons spec (feeds 档案地精 later)
- [ ] 15.9 Party run: acquaintance invite at entrance; shared node; `dungeon_party_runs` + members
- [ ] 15.10 `party-check-manifest.ts` + `resolvePartyCheck()`; per-member dice_roll logs
- [ ] 15.11 Check node `partyCheck` + `partyVariants` schema; UI solo preview + party breakdown (§J)
- [ ] 15.11a Runtime merge `partyVariants` (text/onEnter/outcomes/next); log `party_size` in `dungeon_run_log`
- [ ] 15.11b Publish warn when `supportsParty` and sparse `partyVariants`; gnome prompt co-op checklist
- [ ] 15.12 `POST /api/admin/dungeons/publish` — upsert runtime catalog, no restart (used by gnome-guild later)

## 16. World Revival (world-revival) — Phase 1.5c

- [ ] 16.1 Add revival platform to `hub-plaza`
- [ ] 16.2 Implement d100 revival cost roll + `POST /api/revival` pay and revive
- [ ] 16.3 Insufficient gold flow: list creations, appraise (d100), confirm sell
- [ ] 16.4 Enforce 1 appraisal per creation per 60 minutes
- [ ] 16.5 On sell: delete creation, clear home placements, credit wallet

## 17. World Shop (world-shop) — Phase 1.5c

- [ ] 17.1 Add `shop-manifest.ts` with sample items
- [ ] 17.2 Shop entrance in world scene (NPC or building)
- [ ] 17.3 Shop UI: list, buy, deduct persistent gold, apply effects
- [ ] 17.4 Reject purchases when gold insufficient or when dead (optional)

## 18. Character Gallery (character-gallery) — Phase 1.6

- [ ] 18.1 Implement gallery list API filtered by gallery_visible and canSee
- [ ] 18.2 Build `/gallery` grid page with JRPG detail card on click
- [ ] 18.3 Ensure Creator sees all opted-in entries

## 19. Realtime Presence (realtime-presence) — Phase 2

- [ ] 19.1 Set up WebSocket server (`/ws`) with session auth on layout connect
- [ ] 19.2 Implement dual presence context: `home`, `world:{sceneId}` (dungeon excluded)
- [ ] 19.3 Broadcast map spawn/update/despawn only for same-scene world context
- [ ] 19.4 Render remote adventurer sprites on Phaser map
- [ ] 19.5 Build Creator omniscience panel with home/world labels, locate, chat
- [ ] 19.6 Add heartbeat timeout for stale presence cleanup

## 20. Player Chat (player-chat) — Phase 2

- [ ] 20.1 Implement messages send API with `canSend()` and DB persistence
- [ ] 20.2 Implement history API restricted to `is_admin` only
- [ ] 20.3 Push new messages via WebSocket to online recipients
- [ ] 20.4 Chat from world: click acquaintance sprite
- [ ] 20.5 Chat from home: phone contact list
- [ ] 20.6 Creator chat with full history; initiate from global online list
- [ ] 20.7 Build `/admin/chat-logs` audit UI
- [ ] 20.8 Support receiving live messages on any tab

## 21. Deployment & Verification

- [ ] 21.1 Document Nginx/Caddy config with WebSocket upgrade and HTTPS
- [ ] 21.2 Verify Docker build and first-run seed on clean environment
- [ ] 21.3 Smoke test: dungeon endings → death → revival → shop
- [ ] 21.4 Run validate-code.mjs if harness present

## 22. Agent Life (agent-life) — Phase 2 / V2

- [ ] 22.1 Implement `inventory_items` and soul potion crit-success probabilistic drop on dungeon exit
- [ ] 22.2 Config `SOUL_POTION_DROP.probability` (default 0.35)
- [ ] 22.3 Awakening flow: start / answer / confirm with session expiry
- [ ] 22.4 Server prompt builder from creation + answers; insert `agent_bindings`
- [ ] 22.5 `POST /api/creations/:id/chat` and shared `AgentRouter`
- [ ] 22.6 `POST /api/admin/life/grant` for Creator NPC/item bindings
- [ ] 22.7 Home UI: use potion on **object-only** creation, awakening wizard, chat awakened creation
- [ ] 22.8 Block selling creations with active binding at revival platform

## 23. Gnome Guild (gnome-guild) — V2+ / DISCUSSION

> 需求已记入 `discussion-log.md` §B 与 `specs/gnome-guild/spec.md`；B1 三地精分工已定；实现前需拍板 B2–B10。

- [ ] 23.1 Seed `gnome_plot`, `gnome_engine`, `gnome_archivist` bindings + guild thread (creator + son)
- [ ] 23.2 `/workshop` Gnome Guild panel (Creator) + world `gnome_guild_entrance` facade (all see; adventurers refused)
- [ ] 23.2a Random gnome refusal: AI one-liner via binding + manifest static fallback (incl. **「让我来看看是谁没被邀请。」**); log `gnome_guild_rejection`
- [ ] 23.2b World `tall_folk_guild_entrance` (长身人代码公司); adventurers static refusal **「非法闯入请刷卡。」**; log `tall_folk_guild_rejection`

## 23c. Tall Folk Ops (tall-folk-guild) — V2+ / DISCUSSION

- [ ] 23c.1 Seed `tall_diagnostician`, `tall_engineer`, `tall_releaser` bindings; load at boot (**always-on**, same tier as Son)
- [ ] 23c.2 `/admin/tall-folk` chat + patch/deploy queue; no dormancy gate on open
- [ ] 23c.3 Background log diagnostics (scheduled, rate-limited); issue drafts when Creator offline
- [ ] 23c.4 T0/T1/T2 patch pipeline; T2 requires Creator deploy approve
- [ ] 23.3 `dungeon_script_drafts` + JSON schema validate; engine gnome → draft API only (no repo writes)
- [ ] 23.3a Inject `house-coc` d100 rules into gnome_plot/engine/archivist prompts; tier key validation on publish
- [ ] 23.4 Plot → engine collaboration flow; Son offline facilitation (no publish)
- [ ] 23.5 `gnome_guild_log` persistence; Creator-only read API
- [ ] 23.6 Approval → publish API → `dungeon_scripts` + entrances + announcement + cache invalidate (no restart)
- [ ] 23.7 Archivist tool: aggregate `dungeon_run_log` / `dungeon_ui_log` by dungeon id
- [ ] 23.8 Hotfix draft flow for published dungeons (versioned replace after Creator approve)

## 24. Church, Inventory, Behavior Log, Truth Eye — DISCUSSION (§D)

> 见 `discussion-log.md` §D 与四个 capability spec；实现前需拍板 D1–D9。

- [ ] 24.1 `item_instances` (backpack | home_chest) + personal description field
- [ ] 24.2 Backpack vs chest UI at `/home`; backpack loads into dungeon runs
- [ ] 24.3 Item obtain evaluation prompt + `item_review` log
- [ ] 24.4 Soul potion: separate drink vs apply-to-object; `soul_potion_misdrink` log
- [ ] 24.5 World church scene/entrance + confession board + trait bonus + cooldown
- [ ] 24.6 `player_behavior_log` table + shop/dungeon/church/inventory hooks
- [ ] 24.7 Truth Eye: read logs → adjust attrs → audit; wire attr modifiers into checks and drop rolls
- [ ] 24.8 Home chest UI alongside existing cabinet/creations (keep creations separate per D7)

## 25. SAN, Action Points, Library, Sleep — DISCUSSION (§E)

- [ ] 25.1 `users.san`, `max_san`; `user_debuffs`; `daily_action_points` (max **28**); `ap_dice_purchases_today` (cap **3**)
- [ ] 25.2 Misdrink: consume potion, SAN loss, 3-day 2× SAN loss debuff
- [ ] 25.3 Daily AP reset to 28; block library/sleep/dungeon entry when AP=0
- [ ] 25.4 World library scene + read action + disturbing book roll + logs
- [ ] 25.5 Home sleep action + debuff duration reduction + logs
- [ ] 25.6 Dungeon new-entry AP cost; script SAN loss respects 2× debuff
- [ ] 25.7 Config: daily AP=28, AP dice roll uniform **0–5**, shop dice daily limit **3**
- [ ] 25.8 Shop catalog: action point dice; shop entry/purchase exempt from AP (E7)
- [ ] 25.9 Use dice → roll 0–5, add to daily AP + `ap_dice_use` log (payload includes roll)

## 26. World Bounties — DISCUSSION (§H)

> 见 `discussion-log.md` §H 与 `specs/world-bounties/spec.md`。

- [ ] 26.1 `bounty-manifest` + daily pool refresh; `bounty_board_state` (slot, taker, status)
- [ ] 26.2 World `bounty_board_entrance` + board UI (open / taken / completed)
- [ ] 26.3 Accept: AP deduct, personal daily cap, slot lock; `bounty_accept` log
- [ ] 26.4 Short bounty run UI (reuse dungeon engine, `run_kind=bounty`, wallet gold direct)
- [ ] 26.5 Taker display: `canSee` → name vs 「不相识的冒险者」; Creator always real name
- [ ] 26.6 `bounty_settle` log + completed slot on board
- [ ] 26.7 Config defaults for pool size N and per-user accept cap M (H1)

## 27. World Tavern Table Chat — DISCUSSION (§I)

> 见 `discussion-log.md` §I 与 `specs/world-tavern/spec.md`。

- [ ] 27.1 `tavern_table` interactables in `tavern-hall` Tiled map; seat/unseat state
- [ ] 27.1a Ensure **`li_luang`** seeded; dialogue edited only via `/admin/npcs`
- [ ] 27.2 WS room `room:tavern:{sceneId}:{tableId}`; send only while seated
- [ ] 27.3 Table chat UI distinct from DM / Son / oracle; strangers allowed same table
- [ ] 27.4 Ephemeral delivery (memory/TTL only); **no** `messages` rows; clear client on unseat
- [ ] 27.5 Table roster shows display names for seated strangers; no map canSee grant
- [ ] 27.6 Block persistent DM after tavern-only contact; max **2** seats/table (I1 decided)
- [ ] 27.7 `tavern_menu` — buy 2× duck heart; pending ritual order
- [ ] 27.8 Sit-together invite flow（「你要和我坐同桌吗？」）; same-scene target (I7)
- [ ] 27.9 Dual bond eat → `user_acquaintances` + **two attr bonuses** each; solo eat → **satiety** only
- [ ] 27.10 Ritual cancel: uneaten duck hearts stay with purchaser; solo eat in tavern (I6 decided)
