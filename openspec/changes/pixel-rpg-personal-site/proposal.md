## Why

需要一个像素跑团风格的个人站：访客必须登录才能访问内容；创世主（管理员）管理用户与区域权限；冒险者（用户）可捏人、探索世界地图、在展馆展示角色，并与创世主及其他相识玩家在线互动。站点需接入 AI 神谕（Composer 2.5 / Grok 4.5 via Cursor API），并支持后续部署到云服务器。

## What Changes

- 新建 Next.js 全栈应用，整站登录墙（仅 `/login` 及 auth 接口公开）
- 创世主后台：用户 CRUD、区域（页面）权限矩阵 CRUD、世界公告 CRUD、不相识关系（Party/可见性）CRUD
- 冒险者功能：角色卡（改名号与立绘）、分层捏人、可选入馆展示
- **造物 Tab（`/workshop`）**：创作 CRUD；**（V2+ 讨论）精灵协会**——三精灵 Agent 起草副本、与造物主/之子群聊、对话批准后发布副本+公告
- **家 Tab（`/home`）**：展柜 + 从造物/展柜 **拖动摆放** 到房间；手机聊天
- **大世界 Tab（`/world`）**：多 Scene 观赏社交；**NPC 对话**（静态 / Agent）；**副本入口**
- **副本**：…；死亡 → 复活台 **d100 复活费**；缺钱则 **d100 估价卖造物**（1h/件，需确认）
- **大世界商店**：用 persistent 金币购买物品（入口在大世界）
- 冒险者展馆 Tab：展示 opt-in 公开的角色立绘
- 全局 AI 神谕悬浮窗：登录可用，双模型切换，Cursor API 服务端代理
- 实时多人（Phase 2）：大世界按 scene 互见；在家/在线均可聊天；创世主神视全服在线
- 像素 JRPG 视觉；**左侧边栏**主导航（无顶栏 Tab）
- Docker 化，SQLite 起步，支持云服务器部署

## Capabilities

### New Capabilities

- `auth-session`: 登录墙、session、创世主/冒险者身份、密码认证
- `admin-creator`: 创世主后台——用户管理、区域权限矩阵、不相识/Party 配置
- `character-profile`: 冒险者名号、分层捏人、立绘合成与角色卡
- `page-access`: 页面/区域注册、UserPageAccess 权限校验（路由 + API）
- `world-announcements`: 世界公告 admin CRUD，登录用户全员可见
- `ai-oracle`: 全局神谕浮层（Composer/Grok，工具 AI，与之子分入口）
- `world-map`: `/world` 大世界——多 Scene、scene/portal 门、副本入口
- `world-npcs`: 大世界 **静态** NPC；创世主之子可交互入口
- `creator-son-agent`: 唯一常驻 persona Agent；代管世界、全员可聊、可赠金
- `agent-life`: 赋活（V2）；灵魂药水大成功**概率**掉落、造物觉醒、创世主赋 NPC/物
- `dungeons`: 文字剧本副本、d100、HP/金币、带出战利品
- `world-revival`: 复活台；d100 复活费；缺钱 d100 估价卖造物（1h/件、需确认）
- `trpg-mechanics`: hp/gold/attrs、dungeon_exp、服务端投骰
- `world-shop`: 大世界商店；persistent 金币消费
- `home-space`: `/home` 家——展柜、拖动摆放、hover 描述、活物气泡、手机社交
- `player-creations`: `/workshop` 造物 Tab + 展柜联动；创作物 CRUD、描述、活物台词
- `character-gallery`: 冒险者展馆，opt-in 公开展示，受 `canSee` 过滤
- `realtime-presence`: WS 双 context（home/world+scene）、地图 sprite、创世主神视
- `player-chat`: 结识者互聊（大世界点人/家里手机）；创世主对全服在线；log 仅创世主
- `social-visibility`: `canSee()` 统一规则——不相识则地图/聊天/展馆/id 互不可见
- `pixel-ui-theme`: 像素 JRPG 设计 tokens、对话框、组件皮肤
- `spirit-guild`: **（讨论/V2+）** 造物页精灵协会；剧情/工程/档案三 Agent；群聊+遥测 log；批准 → 副本+公告

### Modified Capabilities

（无——绿field 项目）

## Impact

- 新建 `server/` 或根目录 Next.js 应用及数据库 schema
- 新增依赖：Next.js、Tailwind/shadcn、Phaser 3、WebSocket（如 `ws` 或 socket.io）、bcrypt、Drizzle/Prisma 等
- 环境变量：`CURSOR_API_KEY`、`SESSION_SECRET`、`DATABASE_URL`
- 云部署：Docker、反向代理 WebSocket upgrade、HTTPS
- 资产：像素字体、Tiled 地图、LPC 类 sprite 部件
