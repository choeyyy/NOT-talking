# 设计讨论记录（待续）

> 非正式规格；拍板后回写 `specs/*/spec.md` 与 `design.md`。按时间追加，不删旧条目。

---

## A. 赋活 / 灵魂药水（2026-08-10，未决）

| # | 议题 | 当前 spec 默认 | 待拍板 |
|---|------|----------------|--------|
| A1 | 药水掉落概率 | **0.35**（`SOUL_POTION_DROP.probability`） | 维持 35% / 改 20% / 改 50% |
| A2 | `crit_success` 定义 | ~~待定~~ → **检定档位** `crit_success`（房规 A：`roll` 1–5 且 ≤ DC）；与 `trpg-mechanics` `house-coc` 一致；地精写本同步 |
| A3 | 觉醒造物 vs `phrases[]` | 未写 | **替换** / **并存** / **混合**（idle phrases + 点开 Agent） |
| A4 | 复活台卖已赋活造物 | tasks 22.8 倾向禁止 | 是否禁止有 binding 的 creation 被估价出售 |
| A5 | 之子经济 | 之子可赠金币 | 之子**不可**赠药水；药水仅副本/剧本/admin |
| A6 | 药水适用造物 | **仅静物 `object`** | ~~活物 `creature`~~ → **已决：灵魂药水不可对活物使用** |

**A6 说明（2026-08-11）：** 活物（`kind=creature`）已有 `phrases[]` 随机台词，**不能**消耗灵魂药水做觉醒 Agent。药水觉醒 **仅限** `kind=object` 的静物造物。创世主 admin 赋活 NPC/世界物仍走 `admin/life/grant`，与药水无关。

**相关 spec：** `agent-life`、`dungeons`、`world-revival`、`player-creations`

---

> **用语（2026-08-11）：** 协会三人称 **地精**（非精灵）。代码 id：`gnome_*`；capability **`gnome-guild`**。

## B. 地精协会（2026-08-10 新提案 · 待细化）

### 用户原话摘要

- **入口：** 造物主页（`/workshop`）内设 **地精协会**
- **组成：** **3 个 Agent**（地精）
- **职责：** 地精负责 **产生玩家可用的副本剧本**
- **群聊：** 地精 ↔ **造物主（创世主）** ↔ **造物主之子**（三地精 + 造物主 + 之子 = 工作群）
- **离线：** 造物主不在线时地精 **休眠**；之子可阅历史、留言，**不可** 唤醒地精或 publish（见 §N）
- **审批：** 造物主在 **对话中明确同意** 后
  - 剧本 **发放到副本**（写入 **DB 运行时注册表** `dungeon_scripts`，免重启）
  - **同步更新公告栏**（新世界副本/活动通知）

### 已共识方向（待写进正式 spec）

1. 地精协会是 **V2+** 能力，依赖 `agent_bindings` + 群聊基础设施 + dungeon 脚本存储。
2. 审批主路径是 **群聊内口头/文字同意**，而非仅 admin 后台点按钮（可辅以结构化「确认发布」动作为兜底）。
3. 之子在造物主离线时 **可参与协作文案**，但 **最终发布权在造物主**（之子不能单方面 publish）。
4. **唤醒：** 地精/长身人 **不**随主程序常醒；造物主 **打开对应聊天窗** 后才调用 Agent（见 §N）。
4. 冒险者 **看得见** 大世界地精会议门面，**点不进去** — 交互时地精 **拒入**（JRPG 对话框）；功能面板仍仅造物主（`/workshop` 或世界入口）。

| ~~B12~~ | 大世界地精会议可见性 | **已决**：全员可见；冒险者被拒；造物主可进；拒入 **随机地精 AI 短拒**（失败回退 manifest 静态句）；**canonical 静态拒句：**「让我来看看是谁没被邀请。」 |

### 三地精分工（2026-08-10 已定 · 待实现细节）

| ID | 称谓（建议） | 职责 |
|----|--------------|------|
| `gnome_plot` | **剧情地精** | 设计副本 **剧情**：节点叙事、分支、选项文案、结局线；产出剧情草案供协作 |
| `gnome_engine` | **工程地精** | 把剧情 **落到后端可执行剧本**（符合 `dungeons` JSON schema）；**调整数值**到合理程度（检定 DC、hp/gold 奖惩、exp 门槛、掉落等） |
| `gnome_archivist` | **档案地精** | **管理已发布剧本**；读取并分析玩家跑本 **遥测**：投骰记录、hp/金币扣减流水、通关结算；向协会群反馈平衡/体验问题，驱动修本 |

**协作顺序（建议，可 @ 跳过）：** 剧情地精起草 → 工程地精结构化+调数值 → 档案地精（对已发布本）复盘 → 造物主批准发布/热更。

**日志依赖（档案地精 + 造物主审计）：**

| Log 类型 | 内容 | 消费者 |
|----------|------|--------|
| `dungeon_ui_log` | 副本内 **JRPG 聊天框** 展示/玩家可见叙事与选项流 | 档案地精分析、造物主审计 |
| `gnome_guild_log` | 地精协会 **群聊**（含三地精、造物主、之子） | 档案地精、造物主审计 |
| `tall_folk_guild_log` | 长身人修会群聊 | 造物主审计 |
| `dungeon_run_log` | 结构化副本遥测：节点、**d100 投骰**、hp/gold/attrs 变更、flags、**通关结算**（结局 tier、run_gold 合并、药水掉落等） | 档案地精分析、工程地精调数值 |

> V1 副本可先写 `dungeon_run_log`；地精协会上线前需保证三类 log 齐全。玩家仍不可读历史聊天；**造物主**（及档案地精工具接口）可读。

### 待讨论（下次续聊）

| # | 议题 | 选项 / 备注 |
|---|------|-------------|
| ~~B1~~ | ~~三地精分工~~ | **已定义**：剧情 / 工程 / 档案（见上表） |
| B2 | 「玩家剧本」范围 | ~~全服共用 vs 单人专属~~ → **已决方向：同一剧本；** 结识者 **组队进本**；**不按人数分叉剧情**，仅 **`partyCheck` 调 DC/成功率**（见 §J） |
| B3 | 草案存储 | `dungeon_script_drafts` 表 + JSON schema 校验 vs 纯聊天附件 |
| B4 | 「对话同意」判定 | 关键词 + 造物主消息 / 显式「批准草案 #id」指令 / Son 二次确认 |
| B5 | 公告模板 | 自动标题「新副本：{name}」+ 摘要 / 地精起草公告正文一并待批 |
| B6 | 失败与回滚 | 发布后发现问题：下架副本 + 撤回公告 / 热修版本号 |
| B7 | workshop UI | 协会面板：群聊 + 草案列表 + 状态 + **档案地精分析报告** |
| ~~B8~~ | API 成本 / 唤醒 | **已决**：地精 **不**后台常醒；**仅**造物主 **点开** 地精/长身人 **聊天窗** 后唤醒；关窗即 dormant（无轮询） |
| B9 | 工程地精「落代码」边界 | ~~仅 JSON vs PR~~ → **已决：仅 DB 运行时注册，不改代码、不重启**（见 §B.1） |
| B10 | 档案地精输出 | 仅群聊摘要 vs 结构化 `script_review_reports` 表供工程地精引用 |
| ~~B11~~ | 进行中 run 与热更 | **已决：有人正在跑则 **不更新该 run**；开局钉住 `script_version`；仅新开局读最新版** |

### B.1 运行时剧本接入（2026-08-10 · 架构约束）

**问题：** 若工程地精把剧本写进 `dungeon-manifest.ts` 等代码，发布需 **构建/重启**；重启期间 Agent 不可用，地精协会自我停摆。

**结论：** 地精发布的剧本 **不得** 依赖改代码或重启。采用 **运行时剧本注册表（Runtime Dungeon Registry）**：

| 层 | 来源 | 用途 |
|----|------|------|
| Bootstrap | 仓库内 **示例** JSON + seed migration | 首启可玩样本；**不是**地精发布路径 |
| Runtime | DB `dungeon_scripts` + `dungeon_entrances` | 工程地精产出 → 造物主批准 → **即时生效** |

**工程地精只做：** 写入/更新 `dungeon_script_drafts.script_json` → 批准后经 **Publish API** 晋升到 `dungeon_scripts`（version++），可选写入 `dungeon_entrances`（大世界入口），更新公告。**不**改 `.ts` manifest、**不**触发 deploy/restart。

**服务端：** `DungeonScriptLoader` 按 `dungeon_id` 读 DB；短 TTL 内存缓存 + publish 时 **显式 invalidate**。进行中的 `dungeon_runs` **钉住** 开局时的 `script_version`，避免热更打断跑团。

**大世界入口：** Tiled 里已有 `dungeon_entrance` 可继续引用 `dungeon_id`（解析走 DB）；地精新本可通过 DB 动态入口出现在指定 scene，**无需**改地图资产或重启。

```
工程地精 → dungeon_script_drafts (JSON)
     ↓ 造物主对话同意
POST …/publish → dungeon_scripts (live) + dungeon_entrances? + announcement
     ↓ cache invalidate（无 restart）
下一局 /dungeon/[id] 即加载新剧本
```

### 草案工作流（供讨论）

```
/workshop 地精协会
    │
    ├─ 三地精 agent_bindings（seed）
    │     ├─ gnome_plot      剧情地精 → 叙事/分支/结局
    │     ├─ gnome_engine    工程地精 → schema 剧本 + 数值调优
    │     └─ gnome_archivist 档案地精 → 已发布本复盘 + 读三类 log
    ├─ 群聊 thread：creator + son + gnome×3
    │
    ├─ [起草] 剧情地精 → 工程地精结构化 dungeon_script_draft
    ├─ [离线] 之子可留言、催稿标记；地精 dormant 直至造物主再次 **打开聊天窗**
    ├─ [待批] 草案 status → pending_approval，群聊 @ 造物主
    ├─ [同意] 造物主在群内同意 → validate → publish → 公告
    ├─ [运营] 档案地精读 dungeon_ui / guild / run logs → 分析报告 → 驱动修本
    └─ [已发布] draft.status = published；公告全员可见
```

**相关 capability（草案）：** `gnome-guild` — 见 `specs/gnome-guild/spec.md`

**完整对话归档：** `conversation-log.md`（37 轮，含 OpenSpec 探索至地精协会/运行时剧本讨论）

---

## D. 教堂 / 背包 / 行为 Log / 真理之眼（2026-08-11 · 新提案）

### 用户原话摘要

1. **灵魂药水误喝**：若玩家误喝怎么办？
2. **大世界教堂**：忏悔（类似留言板），忏悔后 **某个特质 +**
3. **物品评价**：获得物品时可输入 **评价**（计入 log）
4. **背包 + 家里箱子**：背包可带进副本；箱子=仓库；两处均可 **打开物品、补充描述**
5. **行为 Log**：物品评价、副本选择、教堂忏悔、商店购买等 **均需记录**
6. **真理之眼**：针对玩家 log **加减属性**；属性影响 **副本检定数值** 与 **获得物品概率**

### 已写入草案 capability

| Capability | 文件 |
|------------|------|
| `world-church` | `specs/world-church/spec.md` |
| `player-inventory` | `specs/player-inventory/spec.md` |
| `player-behavior-log` | `specs/player-behavior-log/spec.md` |
| `truth-eye` | `specs/truth-eye/spec.md` |

### 架构草案

```
玩家行为 → player_behavior_log
              ├─ item_review / item_description_edit
              ├─ dungeon_choice (+ dungeon_run_log 遥测)
              ├─ church_confession
              ├─ shop_purchase
              └─ soul_potion_misdrink

真理之眼 ← 读 log（+ 可选 AI 摘要）→ 调整 users.attrs → truth_eye_adjustment 审计

attrs → trpg 检定修正 + 掉落概率修正（药水等）

物品：item_instances（backpack | home_chest）+ 玩家补充描述 + 获得时评价

灵魂药水：「对静物使用」≠「饮用」；误喝单独动作 + log
```

### 待拍板

| # | 议题 | 选项 / 备注 |
|---|------|-------------|
| D1 | **误喝药水后果** | ~~待定~~ → **已决（§E）**：耗 1 瓶 + 掉 SAN + 3 天 2× 掉 SAN debuff；图书馆/睡觉减 debuff 时长；均耗 AP |
| D2 | 忏悔 **可见性** | 全服留言板 / 仅相识 / 仅造物主可见 |
| D3 | 忏悔 **特质+** 哪个 attr | 新字段 `piety` / 现有 chr·wit / 可配置 |
| D4 | 忏悔 **冷却** | 每日一次 / 每周 / 无冷却 |
| D5 | 真理之眼 **触发** | 玩家主动在大世界交互 / 定时批处理 / 副本 exit 后 |
| D6 | 真理之眼 **实现** | 纯规则表 / AI 读 log 摘要 / 混合 |
| D7 | 背包 vs `creations` | 造物=展柜摆放；**背包物品=副本战利品/商店货**（推荐分离） |
| D8 | 评价是否 **强制** | 获得时可选弹窗 vs 可跳过（spec 默认可跳过） |
| D9 | 箱子容量 | 无限 / 格数上限 / 与背包共享 catalog |

### 与 A6 关系

- 药水 **只能对静物 `object` 觉醒**（A6 已决）
- **误喝**走 `soul_potion_misdrink` 动作，不触发觉醒

---

## E. SAN / 行动点 / 图书馆 / 睡觉（2026-08-11 · 已决方向）

### 误喝灵魂药水（D1 已定）

1. **消耗 1 瓶** 灵魂药水  
2. **立即掉 SAN**（具体数值可配置）  
3. 获得 debuff **`misdrink_frail_mind`**，持续 **3 天**  
   - 期间任何 SAN 下降按 **2×** 结算（相对基础掉幅）  
4. **缩短 debuff 剩余时间**（不能无限刷）：  
   - 大世界 **图书馆看书**（耗 AP；有概率触发 **掉 SAN 的禁书**）  
   - **在家睡觉**（耗 AP）  

### 每日行动点（AP）

- 每名冒险者 **每日行动点**，日切重置（建议 UTC+8 0:00）  
- AP 耗尽 → **不能** 再：看书、睡觉、**新进副本** 等（具体耗 AP 动作见 manifest）  
- 目的：不能靠无限看书/睡觉/刷本在一个日内清 debuff 或肝穿内容  

### 待配置（实现前）

| # | 议题 | 备注 |
|---|------|------|
| E1 | 每日 AP 上限 | ~~待定~~ → **28 点/人/日** |
| E2 | 看书/睡觉各耗 AP & 各减 debuff 多少 | 如各 -4h 剩余 |
| E3 | 误喝即时掉 SAN 数值 | 如 -15 |
| E4 | 禁书触发概率 & 额外掉 SAN | 如 p=0.2, -10 SAN |
| E5 | 「3 天」定义 | 72h 滚动 vs 三个日切 |
| E6 | 副本进行中是否再扣 AP | 建议仅 **新进本** 扣 1 AP |
| E7 | **行动点数色子** | ~~待定~~ → **随机 0–5 AP/颗**；**每日限购 3 个**；商店不耗 AP |

### 行动点数色子（E7 已定，2026-08-11）

- **每日基础 AP：28 点/人**（日切重置，UTC+8 待定）
- AP 不够 → 商店买 **行动点数色子**（金币；**进店/购物不耗 AP**）
- **色子效果：** 使用后 **随机 +0～5** 当日 AP（均匀或权重可配置，默认 uniform 0–5）
- **限购：** 每人 **每日最多买 3 个** 行动点数色子（日切刷新计数）
- 日志：`shop_purchase` + `ap_dice_use`（payload 含 roll 值）

**相关 spec：** `sanity-action-points`、`world-library`、`home-space`（sleep）、`player-inventory`、`dungeons`、`player-behavior-log`、`world-shop`

---

## F. d100 判定 / 写本 Agent 同步（2026-08-11）

### 默认规则 `house-coc`（房规 A + CoC 分档）

与 `specs/trpg-mechanics/spec.md` 一致；**运行时、publish 校验、三地精 prompt 注入** 共用同一套。

| tier key | 中文 | 条件 |
|----------|------|------|
| `crit_failure` | 大失败 | 96–100 且 > effectiveDc |
| `crit_success` | 大成功 | 1–5 且 ≤ effectiveDc |
| `extreme_success` | 极难成功 | ≤ effectiveDc÷5 |
| `hard_success` | 困难成功 | ≤ effectiveDc÷2 |
| `success` | 成功 | ≤ effectiveDc |
| `failure` | 失败 | 其余 |

- 缺 `hard_success` / `extreme_success` 分支 → 回退到 `success`
- 灵魂药水：副本 exit 时 ending/check 解析为 **`crit_success`** 才走药水概率（与 A2 一致）

### 地精协会同步

| 地精 | 写本要求 |
|------|----------|
| 剧情地精 | 大纲里用 **canonical tier 名** 标注分支意图 |
| 工程地精 | JSON `outcomes` **只用** 上表 key；校验失败不可待批 |
| 档案地精 | 遥测按 tier 聚合，反馈工程地精调 DC |

实现：`lib/dungeons/d100-resolver.ts` + `script-schema.ts` + seed prompt 片段 `gnome-d100-rules.md`（服务端注入 `agent_bindings`）。

---

## G. 玩家金币来源（当前 spec 汇总 · 2026-08-11）

钱包 **`users.gold`**（persistent）与副本内 **`run_gold`**（暂存）分离。商店、复活、之子赠金等只动 **wallet**。

### 收入（获得金币）

| 来源 | 说明 | 阶段 | spec |
|------|------|------|------|
| **新建角色** | 配置项默认起始 gold | V1 | `trpg-mechanics` |
| **副本带出** | 剧本节点 `gold: +N` 计入 `run_gold`；**仅成功 exit** 并入 wallet | V1 | `dungeons` |
| **之子赠金** | 创世主之子聊天窗从 `son_wallet_gold` 转给玩家（非自赚，是赠送） | V1 | `creator-son-agent` |
| **复活台卖造物** | 死亡且缺钱复活时，d100 估价后 **确认出售** creation → wallet +gold | V1 | `world-revival`, `player-creations` |
| **悬赏栏** | 大世界短悬赏 + d100；偏加钱；接取耗 AP；每日限量 | 讨论 | `world-bounties` |

### 暂不算「赚取」（未写或未实现）

- 采集 / 玩家交易
- 教堂忏悔、图书馆、真理之眼 **不给 gold**（除非日后剧本节点另写）
- 造物主 admin 可直接改用户数据（运维，非玩法）

### 支出（花金币）

| 用途 | spec |
|------|------|
| 大世界 **商店**（含行动点数色子，每日限购 3） | `world-shop`, `sanity-action-points` |
| **复活台** d100 复活费 | `world-revival` |
| 副本节点 **`gold: -N`**（若剧本写，直接扣 wallet 或 run_gold 见节点配置） | `dungeons` |

### 规则备忘

- 副本进行中 **`run_gold` 不能购物**；须 exit 成功合并进 wallet 后才能在商店花。
- 副本 **失败/死亡** 默认 **不带出** `run_gold`（除非剧本节点例外）。
- 卖造物 **仅** 在复活台死亡流程；活着不能卖。

---

## H. 大世界悬赏栏（2026-08-11 · 新提案）

### 已定方向

1. **地点名：** **悬赏栏**（capability `world-bounties`；地图物件 `bounty_board_entrance`）
2. **玩法：** 类似 **小副本**——短文字节点 + d100（`house-coc`）；结局 **加/扣 persistent gold**，表盘 **偏加钱**
3. **行动点：** **接取** 悬赏扣 AP（与新进副本同级，默认 1 AP/单）
4. **每日限量：**
   - **栏位池：** 每日刷新 N 条悬赏（manifest 配置）
   - **个人上限：** 每人每日最多接 M 单（如 3）
5. **接取记录：** 被接下的悬赏在 **悬赏栏 UI** 显示「已接」；**相识** 冒险者可见 **接取者名号**；**不相识** 仅见 **「不相识的冒险者」**（不暴露 id/立绘）；**造物主** 全视实名
6. **金币：** 不走 `run_gold`，结算 **直接进 wallet**

### 待定

| ID | 问题 |
|----|------|
| H1 | 栏位池 N、个人上限 M 默认值 |
| H2 | 每日刷新时间与 AP 日切是否同一 UTC+8 0:00 |
| H3 | 加/扣钱概率表（建议加 ≥60%、扣 ≤25%） |
| H4 | 进行中悬赏能否放弃 / 超时释放栏位 |
| H5 | 悬赏脚本来源：纯 manifest vs 地精协会日后扩展 |
| H6 | 匿名文案是否统一「不相识的冒险者」或按跑团文案轮换 |

**相关 capability：** `world-bounties` — 见 `specs/world-bounties/spec.md`

---

## I. 酒馆同桌临时对话（2026-08-11 · 新提案）

### 已定方向

1. **地点：** 大世界 **酒馆**（manifest `tavern-hall`，如 **余烬酒馆**）；地图物件 **`tavern_table`**（带 `tableId`）
2. **入座：** 玩家与空椅交互 → **坐桌**；离桌 / 走远 / 断线 → **离席**
3. **对话范围：** **同一桌**（同 `sceneId` + 同 `tableId`）内，**无论 `canSee` / 是否相识**，均可 **同桌聊天**
4. **临时性：** **不写 `messages` 表**；冒险者 **无持久记录**、离桌清空、再坐不恢复；**不能** 借此开 persistent DM
5. **同桌可见名：** 就座期间同桌可见 **display name**（仅桌内 UI）；**不** 获得地图互见、手机联系人、展馆权限
6. **通道：** WS room `room:tavern:{sceneId}:{tableId}`；与神谕、之子、持久 DM **分 UI**
7. **人数：** 每桌 **最多 2 人**；满座拒入并提示

### 鸭心结缘（玩家自结识 · 2026-08-11）

**不在创世主控制下的结识，唯一途径：**

1. 在酒馆 **点两串烤鸭心**（`tavern_grilled_duck_heart` ×2，金币）
2. 对同场景冒险者发起 **「你要和我坐同桌吗？」** 邀请
3. 对方 **接受** → 两人 **同桌**（2 人桌）
4. **各吃一串** → 建立 **`user_acquaintances` 互链** → **酒馆外** 也可 persistent DM / 地图互见 / 手机联系人
5. **结缘成功各吃一串** → 每人 **+两种数值**（manifest 配两个不同 attr，见 I5b）
6. **结缘失败自己吃 / 非结缘自购自吃** → 每串 **只加饱食度**（`satiety`）

**规则：**

- 同桌临时聊天 **仍** 在结缘前可用；结缘 **前** 不能 persistent DM
- **结缘失败**（拒邀 / 离桌 / 超时）：**不退金币**；未吃的鸭心归 **下单者**，可在酒馆 **自己吃掉**（每串 **仅饱食度**）
- 创世主仍可通过 admin **改团 / 直接加结识**（覆盖）
- `canSee` = **同团** OR **`user_acquaintances` 互链**
- 默认新用户建议 **单人团**（陌生人开局），否则全员同团时结缘无意义

### 待定

| ID | 问题 |
|----|------|
| I1 | 每桌最多几人；满座反馈 | ~~待定~~ → **已决：2 人/桌** |
| I2 | 离桌判定：手动按钮 vs 走出半径 |
| I3 | 造物主是否审计同桌聊天（默认 **不长期存储**） |
| I4 | 是否记 aggregate `player_behavior_log`（如 `tavern_table_chat` 仅计数不含正文） |
| I5 | 鸭心效果分类 | ~~待定~~ → **已决：结缘成功各吃一串 = +两种数值；失败自吃 / 自购自吃 = 仅饱食度** |
| I5b | 结缘成功 **哪两种** attr、各 +多少 | 待定（manifest `bond_duck_heart_bonus`） |
| I5c | 饱食度 solo 每串 +多少、`max_satiety` 默认 | 待定 |
| I6 | 结缘失败 heart 处理 | ~~待定~~ → **已决：不退金币；未吃的归购买者，可自己在酒馆 **吃掉**（一串一 buff，两串都吃也行）** |
| I7 | 邀请对象是否必须在 `tavern-hall` 同场景 |

**相关 capability：** `world-tavern` — 见 `specs/world-tavern/spec.md`

---

## J. 副本组队检定（2026-08-11 · 新提案）

### 已定方向

1. **谁可组队：** 仅 **结识** 玩家（`user_acquaintances` 互链或同团）；入口邀请，默认 **最多 4 人**
2. **同一剧本：** **不分** 单人本 / 多人本 id；一个 `dungeon_scripts` 全员共用
3. **人数难度：** ① **`partyCheck`** — baseDc 不变，**人越多 effectiveDc 越高**（默认 +5/人）；② **`partyVariants`** — 地精为 **2+ 人** 写 **不同文案 / 选项 / 后果 / 分支**（不只加 DC）
4. **检定方式：** 每人 **各投 d100**；队伍结果按 `resolution` 聚合（默认 **`best_roll`**）
5. **UI 同屏：** 单人预览 + 队伍检定 + 队伍结果
6. **人数方向：** **人越多越难**（DC Δ 默认 **+5**）
7. **地精分工：** **剧情地精** 大纲标注各节点 `partyVariants` 意图；**工程地精** 落成 JSON；**档案地精** 对比 solo/party 遥测

### 脚本怎么配（工程地精 / 手写的 check 节点）

全局默认：`lib/party-check-manifest.ts`  
节点可选覆盖：`partyCheck` 块（见 `dungeons` spec 示例 JSON）

| 字段 | 含义 | 默认 |
|------|------|------|
| `dc` | 基准难度（单人/预览都用这个数展示） | 必填 |
| `partyCheck.enabled` | 是否启用组队规则 | true |
| `partyCheck.dcDeltaPerExtraMember` | 每多 1 人 DC 变化（**正数 = 更难**） | **+5** |
| `partyCheck.resolution` | `best_roll` / `worst_roll` / `majority_success` / `any_success` | `best_roll` |
| `partyCheck.statMode` | 用谁的属性修 DC：`roller` / `best` | `best` |
| `partyCheck.showSoloPreview` | 是否显示单人预览行 | true |
| `partyCheck.applyEffects` | 后果施加：`each` / `roller` / `leader` | `each` |

### 节点 `partyVariants`（地精必写 · 多人变动）

同一节点可挂数组；服务器取 **≤ 当前人数** 的 **最大** `minPartySize` 条目：

```json
"partyVariants": [
  { "minPartySize": 2, "text": "两人……", "onEnter": { "hp": -2, "applyEffects": "each" } },
  { "minPartySize": 3, "text": "三人……", "next": "other-branch" }
]
```

| 字段 | 多人时作用 |
|------|------------|
| `text` | 替换叙事 |
| `choices` | 替换选项 |
| `onEnter` | 进节点即时后果 |
| `partyCheck` | 覆盖 DC Δ / resolution |
| `outcomes` | 覆盖检定后果 / 下一节点 |
| `next` | 线性节点改跳转 |

剧本根可加 `"supportsParty": true`；发布时 **partyVariants 过少 → 警告**（软门禁）。

**地精：** 剧情地精在大纲里 **逐节点** 写「2 人 / 3 人时发生什么」；工程地精编码进 JSON；不要只调 DC 不写文案。

### UI 示例（baseDc 60，2 人）

```
── 检定：锈锁 (DC 60) ──
单人预览 · 你：🎲 48 → 成功 (DC 60)

队伍检定 (2 人，有效 DC 65 · 人数 +5)：
  艾拉：🎲 42 → 失败
  布兰：🎲 63 → 成功
→ 队伍结果：成功 (best_roll)
```

### 待定

| ID | 问题 |
|----|------|
| J1 | 组队进本 AP：每人 1 还是队长付 |
| J2 | 队员 HP 独立；失败扣血是否全员 `each` 可节点覆盖 |
| J3 | 离线队员：能否异步各投还是必须同时在线 |
| J5 | 支持组队剧本最少要有多少节点带 `partyVariants` | 待定（如关键节点 ≥50%） |

**相关 spec：** `dungeons`, `trpg-mechanics` — `partyCheck` + `resolvePartyCheck()`

---

## K. 像素工坊 AI 识别与放置（2026-08-11 · 新提案）

### 已定方向

1. **位置：** 创世主 **`/admin/studio`**（嵌入 pixel-studio）
2. **MCP 协同画板：** 设计见 `admin-studio`；**无代码原型**（早期 UI 草稿已丢弃）
3. **流程：** 画完 → **AI 识别**（图 + studio 元数据）→ 你 **指定位置** → **确认** → staging → **发布**
4. **识别输出：** `kind`、`label`、`suggestedObjectType`、`tags`
5. **放置：** 显式坐标或自然语言（AI 提案，须确认）
6. **不自动上线；** recognize / place / publish 记入 audit

### MCP 工具（设计稿 · 未实现）

`studio_draw_pixels` 等 — 实现阶段再定 UI 与技术选型。

### 待定

| ID | 问题 |
|----|------|
| K1 | 识别模型：Cursor 多模态 vs 仅 metadata 规则（小图可规则为主） |
| K2 | 自然语言放置是否 V1 就要 |
| K3 | `studio_assets` 表 vs 纯 JSON 文件 staging |

**相关 spec：** `admin-studio` — 见 `specs/admin-studio/spec.md`

---

## L. 跨端兼容 · 缩放 · 手机暗色（2026-08-11 · 用户拍板）

### 已定

| 项 | 口径 |
|----|------|
| **手机 + PC** | V1 壳层与文字页（非 Phaser 可走键盘替代）均可用；侧栏 `<1024px` 折叠为菜单钮 |
| **网页缩放** | 浏览器缩放 **100%–200%** 不破版、不强制横向滚整页 |
| **手机暗色** | 手机默认 dark tokens；尊重 `prefers-color-scheme: dark`；路由切换无白屏闪 |
| **Phaser** | canvas 适配视口；虚拟方向键仍 Phase 2 |

**相关 spec：** `pixel-ui-theme`

---

## M. 长身人修会 · 程序热更 vs 分后端（2026-08-11 · 用户提案）

### 已定方向

1. **角色：** 创世主旗下的 **长身人团队**（与地精对称）— 修世界相关 **机制/代码问题**；冒险者可见门面、**被拒入**（同地精）
2. **地精能热更的：** 仅 **数据**（`dungeon_scripts` 等 DB + cache invalidate）— **不是**改程序
3. **程序分三档：** **T0** DB 配置即时生效 · **T1** 只重启 worker/ws · **T2** 造物主批准 + 滚动 deploy（真改 TS/React）
4. **不能：** 单进程运行中让 Agent **直接改** 生产代码
5. **分后端：** V1 单容器够用；V2+ 建议 **web / ws-gateway / agent-worker** 三进程；**agent-worker 可空闲**，见 §N

### 待定

| ID | 问题 |
|----|------|
| M1 | 长身人入口：`/admin/tall-folk` vs 大世界单独 landmark 名 |
| M2 | T2 deploy：GitHub PR 还是内置 patch bundle |
| M3 | `runtime_patches` 表 schema 与 gnome publish 是否共用 staging |

**相关 spec：** `tall-folk-guild`

---

## N. 主程序常跑 · 造物主视野 · 按需唤醒 Agent（2026-08-11 · 用户拍板）

### 已定

| 项 | 口径 |
|----|------|
| **主程序** | `web` + `ws-gateway` **一直跑**；冒险者正常进 `/world`、家、副本等 |
| **造物主登录** | 看见与冒险者 **同一套** 主要世界与玩家可见页面（`/world`、`/home`…），另加 `/admin`；**不**因登录自动拉起地精/长身人 |
| **地精 / 长身人** | **休眠** 直到造物主 **点击** 对应 **聊天窗/协会面板** → 才 **唤醒**（建 session、可调 Cursor API） |
| **关窗** | 聊天面板关闭 → **先** 聊天记录 + 草案快照落服务器 log → **再** session 结束 → 地精/长身人 dormant |
| **之子** | **常启** — 随主程序启动，冒险者随时可聊；**不**唤醒地精/长身人 |
| **神谕** | 登录用户 **点浮层** 才请求（按需） |

**相关 spec：** `gnome-guild`, `tall-folk-guild`, `admin-creator`, `agent-life`, `creator-son-agent`

### 地精改剧本怎么生效（相对「主程序常跑」）

地精 **Agent 休眠** ≠ 剧本 **不能玩**。已发布剧本在 **DB**，由 **一直跑的后端** 读取：

```
[常跑] 冒险者 /world、副本 API、之子
         │
         ▼
   DungeonScriptLoader ──读──► dungeon_scripts（DB）
         │
         ▼
   新开局副本 → 最新版；进行中 run → 钉住 script_version

[按需] 造物主打开地精聊天窗
         │
         ▼
   地精起草 → dungeon_script_drafts（DB）
         │
         ▼
   造物主对话里批准 → Publish API
         │
         ├─ upsert dungeon_scripts
         ├─ invalidate 缓存
         ├─ 可选 dungeon_entrances + 公告
         └─ **不重启** web/ws/之子
         │
         ▼
   关聊天窗 → 地精再 dormant；新剧本已对 **新开局** 生效
```

---

## O. Agent 安全 · 防抽风（2026-08-11 · 用户拍板）

### 原则

**模型只能「说」和「提案」；真正改世界必须过服务端闸门。**

| 层 | 做什么 |
|----|--------|
| **AgentRouter** | 唯一 Cursor 出口；不信任客户端 prompt |
| **工具白名单** | 之子只能聊+赠金；神谕只聊；地精只能草案+`propose_publish`；长身人只能 patch 草案+`propose_deploy` |
| **人工确认** | publish / patch / deploy / 大额赠金 → **独立确认 API**，聊天里口头批准不算 |
| **Schema 校验** | 剧本 JSON、T0 patch 写入前校验；非法不落库为 live |
| **限流** | 按人/按 session/全局限流；超限不调 API |
| **熔断** | Cursor 挂掉 → 静态 fallback（地精拒入句等） |
| **Kill switch** | 造物主 `/admin` 一键关某类 Agent |
| **审计** | 所有 side-effect 记 log |

**相关 spec：** `agent-safety`

---

## C. 实现前技术项（原有）

- Cursor API `MODEL_MAP`（Composer / Grok model id）
- 创世主地图 sprite：V1 建议玩家不可见，仅神视
- 移动端虚拟方向键 — Phase 2 polish
