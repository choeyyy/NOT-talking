## Context

绿field 项目（`D:\NOTE\PERSONAL`），目标为像素跑团风个人站。访客必须登录；创世主（`is_admin`）管理用户、区域权限、世界公告及玩家相识关系；冒险者捏人、探索可走动世界地图、可选入馆、与相识玩家及创世主互动。AI 神谕经 Cursor API 代理。后续 Docker 部署云服务器。

## Goals / Non-Goals

**Goals:**

- 整站登录墙，RBAC 区域权限，创世主后台完整 CRUD
- 像素 JRPG 视觉与跑团叙事（创世主 / 冒险者 / 区域 / 公告 / 神谕）
- 分层捏人 + 角色卡；`/home` 家 Tab + `/world` 大世界 Tab
- 展馆 opt-in；双 context 在线 presence；`canSee()` 过滤
- 创世主神视、定位、与任意冒险者 DM；登录用户可用 AI 悬浮窗
- SQLite 起步，单 Docker 镜像可部署
- **跨端：** 手机 + PC 可用；侧栏移动端折叠；浏览器缩放 100%–200% 不破版；手机暗色主题 + `prefers-color-scheme: dark`

**Non-Goals:**

- 公开 SEO 落地页、用户自注册、OAuth（V1）
- 完整 RPG 战斗、数值、物品栏
- 访他家（V2）；仅 owner 编辑自家摆放（V1）
- 玩家查看历史聊天记录（log 仅创世主可见）
- AI 对话持久化、RAG、多角色槽（V2 可选）

## Decisions

### 1. 全栈框架：Next.js App Router

**选择：** Next.js 14+（App Router）+ TypeScript + Tailwind + shadcn/ui（像素主题覆盖）

**理由：** 前后端一体、middleware 适合登录墙与路由权限、Layout 承载公告 banner 与 AI/聊天浮层、Docker 部署成熟。

**备选：** Vue + FastAPI（两套部署，个人站过重）

### 2. 数据库：SQLite → PostgreSQL

**选择：** 开发与小规模部署用 SQLite（Drizzle ORM）；`DATABASE_URL` 可切换 Postgres。

**理由：** 个人站用户量小，运维简单；schema 不变迁移。

### 3. 认证：Credentials + httpOnly Session

**选择：** 邮箱+密码（bcrypt/argon2），session cookie（`iron-session` 或 NextAuth Credentials）。

**理由：** admin 创建用户；无 OAuth 需求。API Key 不进浏览器。

### 4. 权限模型：四层规则 + 统一 `canSee()`

```
1. 登录墙：未登录 → 仅 /login、/api/auth/*、静态资源
2. 区域权限：UserPageAccess 控制路由/菜单
3. 世界公告：登录用户全员可读；admin CRUD
4. AI：登录即可用悬浮神谕
5. 社交可见性：canSee(viewer, target) — 不相识则地图/聊天/展馆/id 互不可见
6. 创世主：is_admin → 全视、/admin/*、可与任意人聊天
```

**Page 注册：** 代码内 `site-pages.ts` 启动 sync 至 `pages` 表（含 map 元数据），admin 矩阵勾选。

**不相识：** Party（团）+ **`user_acquaintances`（结识链）**。`canSee` = 同团 **或** 互链。玩家自结识 **仅** 酒馆鸭心结缘（`world-tavern`）；创世主 admin 可改团/直接加链。

**默认新用户：** **单人团**（陌生人开局）；创世主可把多人编入同一团实现批量可见。

### 5. 捏人：LPC 式分层 + Canvas 合成

**选择：** `character_config` JSON（body/hair/top/bottom/colors）+ 客户端 Canvas 合成 PNG → 存 `avatar_url` 或 blob 路径。

**行走：** `/world` 使用 4 方向 walk spritesheet（由 config 生成或模板复用）。

### 6. 大世界：Phaser 3 + Tiled + 多 Scene（仅 `/world`）

**目的：** 观赏 + 社交（聊天、碰面），地图可扩展。

**Scene Manifest：** `lib/world-scene-manifest.ts` 注册 `hub-plaza`（默认）、`garden-view`、`tavern-hall`、`shrine-outer`、`portrait-hall` 等。

**两种门：**

| 类型 | 行为 |
|------|------|
| `scene_door` | 同 Tab 内 Phaser 切 Scene |
| `portal_door` | 离开 world → Next.js 功能页 |
| `dungeon_entrance` | 离开 world presence → `/dungeon/[id]` |
| NPC 交互 | 打开对话 UI（static / agent） |

**NPC（admin / runtime registry）— 静态 + 之子入口：**

- Seed **`li_luang`** · `tavern-hall` · **`Li-Luang`** · grandmother · admin: **dialogue** (AA drinks) + **player address** (乖孙)
- 创世主之子 — 独立 agent，非 static NPC

```typescript
// 普通 NPC — static；li_luang 见上；其余由 /admin/npcs 维护
// 创世主之子 — agent binding + hub-plaza 等入口
```

**Agent 体系：**

| 实体 | Phase | 赋活方式 |
|------|-------|----------|
| 创世主之子 | V1 | seed 固定 binding |
| 神谕 | V1 | 工具，无 binding |
| 造物 | V2 | 灵魂药水 + 觉醒三 step |
| NPC/世界物品 | V2 | 创世主 `admin/life/grant` |
| 地精×3 | V2+ | seed 固定 binding；见下表 |

**三地精（地精协会）：**

| binding id | 角色 | 职责 |
|------------|------|------|
| `gnome_plot` | 剧情地精 | 剧情、节点叙事、分支与结局设计 |
| `gnome_engine` | 工程地精 | 剧本 JSON 落库、schema 校验、数值调优（DC/hp/gold/exp） |
| `gnome_archivist` | 档案地精 | 已发布剧本管理；分析投骰/hp·金币流水/通关结算；依赖三类 log |

**地精协会（V2+）：** `/workshop` 造物主面板 + 大世界 `gnome_guild_entrance`（全员可见）；冒险者点击 → **随机地精 AI 短拒**（失败回退 manifest 静态句）；造物主可进。详见 `discussion-log.md` §B、`specs/gnome-guild/spec.md`。

**赋活后端：** 见 `specs/agent-life/spec.md` — `agent_bindings` + `awakening_sessions` + shared `AgentRouter`.

**之子（V1）：** `son_wallet_gold` admin 充值；`POST /api/son/chat`；聊天赠金。

**Ideas 保留：** 副本 GM Agent、wit 影响估价、商店 broker。

**运行时剧本（Runtime Dungeon Registry）：** 地精/工程路径 **只写 DB**，publish 后 **免重启** 生效。详见 `discussion-log.md` §B.1。

**教堂 / 背包 / 行为 Log / 真理之眼（§D）：** …

**SAN / 行动点（§E）：** 每日 **28 AP**；误喝 debuff；图书馆/睡觉耗 AP；商店不耗 AP；**行动点数色子** 使用随机 **+0～5**，**每日限购 3 个**。

**灵魂药水（V2）：** 副本结局 `crit_success` → `roll < 0.35` → `inventory +1 soul_potion`。**仅静物 `object` 可觉醒**；活物不可；误喝单独 log。

**副本（文字剧本跑团）：**

```
/world 副本入口 ──▶ /dungeon/[id]
                      │
                      ├─ 节点：叙事文本 / 选项 / d100 检定（可选 partyCheck：同 baseDc，**人越多 effectiveDc 越高**）
                      ├─ 结识者组队：同一 run；partyCheck（人越多 DC 越高）+ partyVariants（地精写多人节点变动）
                      ├─ HP：wallet hp 即时扣加
                      ├─ attrs：wallet 属性 ±（力敏智魅等）
                      ├─ dungeon_exp：仅本 run，决定结局分支
                      ├─ 金币：run_gold 累计，成功 exit 并入 wallet
                      └─ 多结局：按 exp/attrs/flags 条件解析

**死亡 → 复活台（d100 复活费 + 卖造物）：**

```
副本 hp≤0  →  is_dead  →  /world 复活台
              │
              ├─ 🎲 投 d100 → 算出复活费（服务端公式）
              ├─ 金币够 → 确认 → 扣费复活
              └─ 不够 → 选造物 → 🎲 估价（每造物 1h 一次）
                        → 显示报价 → 玩家确认卖/不卖
                        → 卖出加金币，重复直到够复活费
```

**估价公式（示例，可配置）：** `offer = roll * 3`（1–100 → 3–300 金）  
**复活费公式（示例）：** `cost = roll * 5`（1–100 → 5–500 金）

**表字段：** `creations.last_appraised_at`, `last_appraised_value`

**属性默认（可配置）：** `str` `dex` `wit` `cha`，初始 10；侧栏/角色卡展示。

**结局示例：**

| 条件 | 结局 |
|------|------|
| dungeon_exp ≥ 80 | 完美脱身 |
| dungeon_exp ≥ 40 | 普通脱身 |
| else | 狼狈逃出 |

**d100 默认档位（可 per-node 覆盖）：**

| 骰值相对 DC | 档位 |
|-------------|------|
| ≤ DC−20 或 96–100 | 大失败 |
| DC−19 … DC−1 | 失败 |
| DC … DC+19 | 成功 |
| ≥ DC+20 且 ≤ 95 | 大成功 |

（具体 band 实现时写入 `lib/d100-resolver.ts`，文档与 spec 一致。）

**脚本节点示例：**

```json
{
  "id": "trap",
  "text": "机关索链从暗处射出……",
  "check": { "dc": 55 },
  "outcomes": {
    "crit_success": { "text": "你闪开了。", "next": "safe", "gold": 5 },
    "success": { "text": "擦伤。", "hp": -5, "next": "hurt" },
    "fail": { "text": "被击中。", "hp": -15, "next": "bad" },
    "crit_fail": { "text": "重伤倒地。", "hp": -999, "next": "defeat" }
  }
}
```

**冒险者 persistent 属性（`player_stats` 或 users 列）：**

- `hp`, `max_hp`, `gold`（wallet；副本 **HP 直接用 wallet**，金币 exit 才合并 run_gold）

**商店（大世界 `hub-plaza` 等）：**

- `shop-manifest`：id, name, price, effect（如 heal 20 hp）
- 交互 shop NPC / 建筑 → 商店 UI；只扣 **persistent gold**
- 副本内 run_gold 未结算前不可消费

**副本 UI：** V1 以 **文字 log + 投骰按钮** 为主；可选轻量 Phaser 背景，非必须走动。

**Presence：** 进副本 despawn 大世界 sprite。

### 7. 家：/home Tab + 展柜与摆放

**目的：** 在线社交、展示个人创作、布置私人空间。

**双入口：**

| 入口 | 路径 | 作用 |
|------|------|------|
| **造物 Tab** | `/workshop` | 创建/编辑/删除、描述、活物台词、sprite |
| **家 Tab** | `/home` | 展柜 + **拖入房间摆放**、hover、活物气泡、手机 |

同一 `creations` 数据源；`/home` 展柜提供「前往造物 →」快捷链。

**`/home` 房间：**

**创作物 `creations` 表：**

| 字段 | 说明 |
|------|------|
| `name` | 物品名 |
| `description` | hover 展示的长描述 |
| `kind` | `object` 静物 / `creature` 活物 |
| `sprite_url` | 像素图（V1：模板+配色或上传） |
| `phrases` | JSON 字符串数组，仅活物；随机说一句 |

**`home_config.placements`：**

```json
{ "placements": [{ "creationId": "uuid", "x": 120, "y": 80, "z": 1 }] }
```

**活物台词：** 客户端定时器（如 20–60s 随机间隔）→ 从 `phrases` 抽一句 → JRPG 气泡在 sprite 上方。仅 **主人在 `/home`** 时触发（V1）。

**展柜 vs 房间：** 展柜是管理 UI；同一 creation 可在展柜展示且/或摆进房间。删除摆放不删 creation。

```
/home 房间
├── 🗄 展柜（与 /workshop 同步）→ 拖到房间
├── 🔗 「造物」→ /workshop
├── 📱 手机 → 在线结识者聊天
└── 房间画布 → hover 描述；活物随机台词
```

**V1 创作入口：** `/workshop` 完整表单；`/home` 以摆放为主，不全量替代编辑。

**Presence：** `context=home`；默认登录 redirect `/home`。

### 7b. 创作与捏人的关系

- **捏人（character_config）**：冒险者自身立绘，用于地图/展馆/头像
- **创作物（creations）**：可多个，展柜与家里摆放，可含活物台词
- 后期可选：从捏人导出 sprite 存为 creation（非 V1 必须）

### 8. 实时层：WebSocket + 双 Context

**选择：** 登录后 layout 级 WS；上报 presence：

```typescript
{ context: 'home' }
{ context: 'world', sceneId: 'hub-plaza', x, y }
```

**房间：**

```
room:world:{sceneId}   → 地图 sprite 广播（canSee + 同 scene）
room:online            → 全局在线 registry（手机列表、创世主神视）
```

**创世主神视：** 列表显示 `在家` / `大世界·{sceneLabel}`；仅 world 可定位。

**坐标：** world 10–20Hz 节流；heartbeat 3–5s cleanup。

### 9. 聊天：持久化 DM + WS 推送 + 创世主独占 log

**选择：** `messages(from_user_id, to_user_id, body, created_at)` 全量落库；发送经 REST 或 WS；不相识 → 403。

**聊天规则：**

```
结识者  →  大世界里点 sprite 开聊 / 家里用手机选在线结识者
不相识  →  403
创世主  →  全服在线（家+大世界）可发起聊天
```

**API：** 发送消息时 `canSend(from, to)`：`is_admin(from)` → 允许；否则要求 `canSee(from,to) && canSee(to,from)`。冒险者回复创世主：允许（会话已建立或收到 Creator 消息后）。

**Log 可见性：**

```
冒险者  → 仅实时：对话框打开时 WS 推新消息；刷新/重开不拉历史
创世主  → 实时 + 任意会话全量历史（/admin/chat-logs 或聊天 UI 内加载）
```

**API：** `GET /api/chat/history` 或 `/api/admin/chat-logs` **仅 `is_admin`**；冒险者调用一律 403。

**UI：** 与 AI 神谕分离——「神谕之环」vs「冒险者交谈」；任意 Tab 可收实时消息（不仅限地图）。

### 10. AI：Cursor API 服务端代理

**选择：** `POST /api/ai/chat` SSE 流式；`CURSOR_API_KEY` 仅服务端；模型映射表 `composer-2.5` / `grok-4.5`；登录校验 + 可选日限流。

### 11. 视觉：像素 JRPG 主题层 + 侧栏导航

**选择：** 像素字体（中文点阵 + Press Start 2P）、阶梯 box-shadow 边框、JRPG 对话框组件、CSS `image-rendering: pixelated`；shadcn 组件皮肤替换。

**布局：** 登录后 **左侧边栏** 主导航（家、造物、世界、副本、展馆、公告、角色）；**创世主** 额外入口 **⚙ 后台** → `/admin/*`。**不用顶栏 Tab**。

**创世主后台（`/admin`）** — 统一指挥台，非冒险者功能集中在此：

```
/admin
├── 神视 / Dashboard     — 在线、定位、快捷聊天
├── 冒险者 / 区域 / 公告
├── 像素工坊 /studio     — 场景搭建 + AI 识别 + 指定位置放置（embed pixel-studio）
├── 场景与入口 /scenes   — manifest、副本入口发布
├── Log                  — chat-logs · behavior-logs · dungeon 遥测
├── 之子 /son            — son_wallet、赠金审计、Agent 设置
├── 地精协会 /gnome-guild — 群聊、草案、发布剧本
├── 赋活 /life           — V2+
└── 预览玩家页           — 跳转 /home /world /workshop …（全站可见）
```

冒险者 **不能** 进 `/admin`；场景 **只在后台搭**，玩家在 `/world` 玩。捏人 `/profile`、造物 `/workshop` 仍在玩家侧。

```
┌──────────┬────────────────────────────────┐
│ 侧栏     │  [世界公告 banner 可选]         │
│ 🏠 家    │                                │
│ 🔨 造物  │      主内容（/world 等）        │
│ 🗺 世界  │                                │
│ ⚔ 副本   │                    [神谕][聊天] │
│ …        │                                │
│ ⚙ 后台   │  ← 仅创世主：/admin 全功能      │
└──────────┴────────────────────────────────┘
```

移动端：侧栏可折叠为像素菜单钮（**V1 兼容**，见 `pixel-ui-theme`）。整站暗色主题为默认；手机端 dark tokens + 尊重 `prefers-color-scheme: dark`；布局须兼容浏览器缩放至 200%。

### 13. 副本剧本：运行时注册表（免重启）

**选择：** 可玩剧本以 DB **`dungeon_scripts`** 为权威来源；`DungeonScriptLoader` 按 id 加载 JSON；地精 Publish **只写 DB + invalidate 缓存**，不修改仓库 manifest、不重启进程。

**Bootstrap：** 仓库内示例 JSON 仅用于 **seed migration** 灌入首条 `dungeon_scripts`；之后地精/造物主热更均走 DB。

**版本：** `dungeon_scripts.version` 递增；**有人正在跑的 run 不更新**——`dungeon_runs.script_version` 开局钉住，整局沿用旧剧本；仅 **新开局** 加载 catalog 最新版。

**入口：** `dungeon_entrances` 表（scene_id, position, dungeon_id, label）；Tiled 静态 `dungeon_entrance` 与 DB 入口 **合并解析**；新本可仅 DB 挂入口。

**工程地精边界：** 只产出/更新 `dungeon_script_drafts` 与校验后的 JSON；**禁止**生成 TypeScript、migration 或要求 redeploy 的制品。

### 14. 长身人修会 vs 地精：程序变更怎么「热更」（2026-08-11）

**叙事对称：** **地精**（矮）写 **内容**；**长身人**（高）修 **世界运行机制**（配置、API 行为、前后端缺陷）。

**核心结论：** 和地精一样 **能免重启的，只有写 DB / 运行时注册表 + 缓存失效**。**TypeScript / React 真改代码 = 冷部署**，不能在同一进程里像改 JSON 剧本那样 live patch。

| 档位 | 叫什么 | 例子 | 怎么更 | 停机 |
|------|--------|------|--------|------|
| **T0 热更** | Runtime config | 场景门目标、NPC 台词 patch、`feature_flags`、副本 cache invalidate | 写 DB → `invalidate` | 无 |
| **T1 温更** | 子进程重启 | Agent prompt、WS 广播规则、队列 worker | 只重启 **`agent-worker`** 或 **`ws-gateway`** | 数秒；WS 重连 |
| **T2 冷更** | 代码发布 | 改 API 路由、React 页、migration | 长身人出 **patch/PR 草案** → 造物主批准 → CI 构建 → **滚动替换 `web` 容器** | ~30s 滚动；进行中副本仍钉版本 |

**禁止：** 长身人 Agent **直接**改生产机上的 `.ts`/`.tsx` 或 exec 重启整站（安全 + 可审计）。

**要不要分几个后端？**

| 阶段 | 建议 |
|------|------|
| **V1 个人站** | **单容器** Next（HTTP + WS 同进程）即可；接受 T2 时全站短暂重启 |
| **V2+（按需 Agent）** | Docker Compose **三进程**：`web`、`ws-gateway` **常跑**；`agent-worker` **常载之子** + guild 仅 session 活跃时处理 |

```
  [常跑] web + ws  ──► 冒险者 + 造物主看 /world 等
  [常启] 之子      ──► 随主程序启动；冒险者开聊即应
  [按需] 地精/长身人 ◄── 造物主点开协会聊天窗 ──► guild session
                     关窗 ──► 写 log + flush ──► dormant
```

```
                    ┌─────────────┐
  冒险者浏览器 ─────►│ web (Next)  │◄─── T2 滚动发布（前后端 bundle）
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────────┐
        │ SQLite/  │ │ws-gateway│ │agent-worker  │
        │ Postgres │ │ T1 可单杀 │ │之子常启+guild按需│
        └──────────┘ └──────────┘ └──────────────┘
              ▲
              └── T0：dungeon_scripts / scene_drafts / runtime_patches 写 DB
```

**长身人三地精式分工（草案）：** 诊断长身人（读 log 开 issue）→ 工程长身人（出 T0 JSON 或 T2 patch）→ 发布长身人（排队 deploy；T2 须造物主点批准）。

### 15. 运行时：主程序常跑 · 造物主视野 · Agent 按需唤醒（2026-08-11）

**选择：**

- **常跑：** HTTP + WS + 大世界 + 玩家页；Docker/进程 **不因无人登录而退出**
- **造物主登录：** 与冒险者相同的 **主要世界与可见页面**（可进 `/world` 看地图、进 `/home` 等），外加 `/admin` 神视与后台；**登录事件不触发** 地精/长身人 Cursor 调用
- **按需唤醒：** 地精协会、长身人修会 — 仅当造物主 **打开** 对应 **聊天窗/协会 UI** 时创建 guild session；**关闭面板** 时 **先落 log + .flush 会话结果**，再结束 session、**禁止** 关窗后台轮询
- **之子常启：** 随主程序 **一直启动**；造物主不在线时冒险者仍可找之子聊天；之子 **不** 唤醒地精/长身人
- **神谕：** 登录用户 **点浮层** 才请求（按需）

**相关 spec：** §N `discussion-log.md`；`tall-folk-guild`、`gnome-guild`（§13 地精 T0 边界）

### 12. 项目结构（建议）

```
app/
  (auth)/login/
  (protected)/
    home/           # 家 Tab，手机社交
    world/          # 大世界 Phaser
    gallery/
    announcements/
    profile/
  admin/
lib/
  world-scene-manifest.ts
  dungeons/
    script-loader.ts   # DB runtime load + cache invalidate
    script-schema.ts   # JSON schema + tier key validate（地精/engine/publish 共用）
    d100-resolver.ts   # house-coc 共享判定
    gnome-d100-rules.md # 注入三地精 system prompt 的规则摘要
  home/             # 家 UI（V1 DOM 房间）
```

## Risks / Trade-offs

| 风险 | 缓解 |
|------|------|
| Phaser + WS 增加复杂度与 bundle | 动态 import；Phase 分 deliver |
| 按人过滤广播 CPU | 用户数 <30 可接受；后期 Redis pub/sub |
| Cursor API 模型 id 不确定 | `.env.example` + 可配置 MODEL_MAP |
| 地精 publish 若依赖代码重启则 Agent 停摆 | **Runtime Dungeon Registry** — DB 剧本 + cache invalidate（§13） |
| Guild Agent API 空烧 | **按需唤醒** — 仅造物主打开协会聊天窗（§N）；关窗 dormant；**之子除外常启** |
| Agent 抽风 / 越权 / 空烧 API | **`agent-safety`** — AgentRouter、工具白名单、发布/部署须确认、限流、熔断、kill switch |
| 像素中文字体可读性 | 正文 16px+；长文混用半像素字体 |
| WS 云部署穿透失败 | 文档化 Nginx upgrade；Caddy 备选 |
| Party 无法表达同团两人不见 | V2 加 pairwise 例外表 |

## Migration Plan

1. Phase 1：auth、admin、page-access、announcements、profile/捏人、pixel-ui、ai-oracle
2. Phase 1.5a：`/home` 家 + 手机 + 展柜/创作/摆放（见 player-creations）
3. Phase 1.5b：`/world` 多 Scene 大世界
4. Phase 1.6：gallery + opt-in
5. Phase 2：realtime-presence + player-chat + social-visibility
6. Phase 3：访他家、壁纸/家具模板、从捏人导出 creation（可选）

**部署：** Docker Compose（app + volume for SQLite/uploads）；环境变量注入；首 admin seed 脚本。

**回滚：** 数据库 migration 版本化；WS 可独立关闭，站点降级为单机地图。

## Open Questions

见 **`discussion-log.md`**（赋活 §A、地精协会 §B、技术项 §C）。摘要：

- **赋活：** 药水概率、crit_success 定义、静物觉醒 UI、复活台卖赋活静物、之子赠金；~~活物用药~~（A6 已决）
- **地精协会：** B2/B4/B5/B6/B8/B10 等
- **教堂/真理之眼：** 误喝后果、忏悔可见性、Truth Eye 触发与实现（§D）
- Grok 4.5 是否与 Composer 2.5 共用同一 Cursor API endpoint（仅换 model 参数）——实现时对照 Cursor 文档填写 `MODEL_MAP`
- 创世主在地图上对玩家是否可见特殊 sprite，或完全隐形仅神视列表——建议 V1：玩家看不见创世主，创世主看见全员
- 移动端虚拟方向键——Phase 2 polish（**布局/缩放/暗色** 仍属 V1，见 `pixel-ui-theme`）
