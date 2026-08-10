# 设计讨论记录（待续）

> 非正式规格；拍板后回写 `specs/*/spec.md` 与 `design.md`。按时间追加，不删旧条目。

---

## A. 赋活 / 灵魂药水（2026-08-10，未决）

| # | 议题 | 当前 spec 默认 | 待拍板 |
|---|------|----------------|--------|
| A1 | 药水掉落概率 | **0.35**（`SOUL_POTION_DROP.probability`） | 维持 35% / 改 20% / 改 50% |
| A2 | `crit_success` 定义 | 结局 tier = critical success 时 roll | **A** 剧本结局标 tier / **B** d100 极值解锁 / 混合 |
| A3 | 觉醒造物 vs `phrases[]` | 未写 | **替换** / **并存** / **混合**（idle phrases + 点开 Agent） |
| A4 | 复活台卖已赋活造物 | tasks 22.8 倾向禁止 | 是否禁止有 binding 的 creation 被估价出售 |
| A5 | 之子经济 | 之子可赠金币 | 之子**不可**赠药水；药水仅副本/剧本/admin |

**相关 spec：** `agent-life`、`dungeons`、`world-revival`、`player-creations`

---

## B. 精灵协会（2026-08-10，新提案 · 待细化）

### 用户原话摘要

- **入口：** 造物主页（`/workshop`）内设 **精灵协会**
- **组成：** **3 个 Agent**（精灵）
- **职责：** 精灵负责 **产生玩家可用的副本剧本**
- **群聊：** 精灵 ↔ **造物主（创世主）** ↔ **造物主之子**（三精灵 + 造物主 + 之子 = 工作群）
- **离线：** 造物主可能不在线；精灵（及/或之子代管）**可继续起草剧本**
- **审批：** 造物主在 **对话中明确同意** 后
  - 剧本 **发放到副本**（写入 **DB 运行时注册表** `dungeon_scripts`，免重启）
  - **同步更新公告栏**（新世界副本/活动通知）

### 已共识方向（待写进正式 spec）

1. 精灵协会是 **V2+** 能力，依赖 `agent_bindings` + 群聊基础设施 + dungeon 脚本存储。
2. 审批主路径是 **群聊内口头/文字同意**，而非仅 admin 后台点按钮（可辅以结构化「确认发布」动作为兜底）。
3. 之子在造物主离线时 **可参与协作文案**，但 **最终发布权在造物主**（之子不能单方面 publish）。
4. 冒险者 **不进入** 精灵协会群；他们通过大世界副本入口 + 公告得知新本。

### 三精灵分工（2026-08-10 已定 · 待实现细节）

| ID | 称谓（建议） | 职责 |
|----|--------------|------|
| `spirit_plot` | **剧情精灵** | 设计副本 **剧情**：节点叙事、分支、选项文案、结局线；产出剧情草案供协作 |
| `spirit_engine` | **工程精灵** | 把剧情 **落到后端可执行剧本**（符合 `dungeons` JSON schema）；**调整数值**到合理程度（检定 DC、hp/gold 奖惩、exp 门槛、掉落等） |
| `spirit_archivist` | **档案精灵** | **管理已发布剧本**；读取并分析玩家跑本 **遥测**：投骰记录、hp/金币扣减流水、通关结算；向协会群反馈平衡/体验问题，驱动修本 |

**协作顺序（建议，可 @ 跳过）：** 剧情精灵起草 → 工程精灵结构化+调数值 → 档案精灵（对已发布本）复盘 → 造物主批准发布/热更。

**日志依赖（档案精灵 + 造物主审计）：**

| Log 类型 | 内容 | 消费者 |
|----------|------|--------|
| `dungeon_ui_log` | 副本内 **JRPG 聊天框** 展示/玩家可见叙事与选项流 | 档案精灵分析、造物主审计 |
| `spirit_guild_log` | 精灵协会 **群聊**（含三精灵、造物主、之子） | 档案精灵、造物主审计 |
| `dungeon_run_log` | 结构化副本遥测：节点、**d100 投骰**、hp/gold/attrs 变更、flags、**通关结算**（结局 tier、run_gold 合并、药水掉落等） | 档案精灵分析、工程精灵调数值 |

> V1 副本可先写 `dungeon_run_log`；精灵协会上线前需保证三类 log 齐全。玩家仍不可读历史聊天；**造物主**（及档案精灵工具接口）可读。

### 待讨论（下次续聊）

| # | 议题 | 选项 / 备注 |
|---|------|-------------|
| ~~B1~~ | ~~三精灵分工~~ | **已定义**：剧情 / 工程 / 档案（见上表） |
| B2 | 「玩家剧本」范围 | 全服共用新本 / 按 Party 定制 / 单人专属实例？ |
| B3 | 草案存储 | `dungeon_script_drafts` 表 + JSON schema 校验 vs 纯聊天附件 |
| B4 | 「对话同意」判定 | 关键词 + 造物主消息 / 显式「批准草案 #id」指令 / Son 二次确认 |
| B5 | 公告模板 | 自动标题「新副本：{name}」+ 摘要 / 精灵起草公告正文一并待批 |
| B6 | 失败与回滚 | 发布后发现问题：下架副本 + 撤回公告 / 热修版本号 |
| B7 | workshop UI | 协会面板：群聊 + 草案列表 + 状态 + **档案精灵分析报告** |
| B8 | API 成本 | 三精灵唤醒策略：仅 @mention / 草案阶段轮询 / 档案精灵定时批处理 |
| B9 | 工程精灵「落代码」边界 | ~~仅 JSON vs PR~~ → **已决：仅 DB 运行时注册，不改代码、不重启**（见 §B.1） |
| B10 | 档案精灵输出 | 仅群聊摘要 vs 结构化 `script_review_reports` 表供工程精灵引用 |
| ~~B11~~ | 进行中 run 与热更 | **已决：有人正在跑则 **不更新该 run**；开局钉住 `script_version`；仅新开局读最新版** |

### B.1 运行时剧本接入（2026-08-10 · 架构约束）

**问题：** 若工程精灵把剧本写进 `dungeon-manifest.ts` 等代码，发布需 **构建/重启**；重启期间 Agent 不可用，精灵协会自我停摆。

**结论：** 精灵发布的剧本 **不得** 依赖改代码或重启。采用 **运行时剧本注册表（Runtime Dungeon Registry）**：

| 层 | 来源 | 用途 |
|----|------|------|
| Bootstrap | 仓库内 **示例** JSON + seed migration | 首启可玩样本；**不是**精灵发布路径 |
| Runtime | DB `dungeon_scripts` + `dungeon_entrances` | 工程精灵产出 → 造物主批准 → **即时生效** |

**工程精灵只做：** 写入/更新 `dungeon_script_drafts.script_json` → 批准后经 **Publish API** 晋升到 `dungeon_scripts`（version++），可选写入 `dungeon_entrances`（大世界入口），更新公告。**不**改 `.ts` manifest、**不**触发 deploy/restart。

**服务端：** `DungeonScriptLoader` 按 `dungeon_id` 读 DB；短 TTL 内存缓存 + publish 时 **显式 invalidate**。进行中的 `dungeon_runs` **钉住** 开局时的 `script_version`，避免热更打断跑团。

**大世界入口：** Tiled 里已有 `dungeon_entrance` 可继续引用 `dungeon_id`（解析走 DB）；精灵新本可通过 DB 动态入口出现在指定 scene，**无需**改地图资产或重启。

```
工程精灵 → dungeon_script_drafts (JSON)
     ↓ 造物主对话同意
POST …/publish → dungeon_scripts (live) + dungeon_entrances? + announcement
     ↓ cache invalidate（无 restart）
下一局 /dungeon/[id] 即加载新剧本
```

### 草案工作流（供讨论）

```
/workshop 精灵协会
    │
    ├─ 三精灵 agent_bindings（seed）
    │     ├─ spirit_plot      剧情精灵 → 叙事/分支/结局
    │     ├─ spirit_engine    工程精灵 → schema 剧本 + 数值调优
    │     └─ spirit_archivist 档案精灵 → 已发布本复盘 + 读三类 log
    ├─ 群聊 thread：creator + son + spirit×3
    │
    ├─ [起草] 剧情精灵 → 工程精灵结构化 dungeon_script_draft
    ├─ [离线] 之子可回复、催稿、整理草案；不可 approve
    ├─ [待批] 草案 status → pending_approval，群聊 @ 造物主
    ├─ [同意] 造物主在群内同意 → validate → publish → 公告
    ├─ [运营] 档案精灵读 dungeon_ui / guild / run logs → 分析报告 → 驱动修本
    └─ [已发布] draft.status = published；公告全员可见
```

**相关 capability（草案）：** `spirit-guild` — 见 `specs/spirit-guild/spec.md`

**完整对话归档：** `conversation-log.md`（37 轮，含 OpenSpec 探索至精灵协会/运行时剧本讨论）

---

## C. 实现前技术项（原有）

- Cursor API `MODEL_MAP`（Composer / Grok model id）
- 创世主地图 sprite：V1 建议玩家不可见，仅神视
- 移动端虚拟方向键 — Phase 2 polish
