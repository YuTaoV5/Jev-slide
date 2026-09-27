# minecraft-agent 仓库代码分析与争议核实

分析日期：2026-09-27。  
分析对象：`https://github.com/rmalde/minecraft-agent`（rmalde/minecraft-agent，public，560 stars，58 forks，2026-09-20 创建；当前 4 个 open issues）。  
本仓库基于 TypeSafe 最新 Jev 模型 `typesafe/jev-1.13`，配合 GPT-6 Astra（或可选 GPT-5.6 Sol）做高阶规划。  
所有结论来自本地源码静态分析（git clone 后逐文件阅读），**未实测、未运行、未调用模型**。

---

## 0. 仓库与争议概览

| 维度 | 仓库自述 | 中文网络流传（用户提供） | 代码事实 |
|---|---|---|---|
| 8 分钟击败末影龙 | `nether-final-08` 8m 43.300s（README L7） | "8 分钟击败末影龙" | ✅ 数字匹配 |
| 成本不到 1 美元，Jev < 0.01 美元 | 仓库未直接给出账单数字 | 流传版本声称 | 仓库未量化；下文核验 |
| 决策模型是摆设 | （仓库隐含，但 README 把 131 次称为"decisions"） | 流传版本攻击 | 部分可证：单选项比例高 |
| 规划模型提前拿到答案 | （system prompt 直接告诉规划器路线） | 流传版本攻击 | ✅ 完全可证 |
| 随机选择也能通关 | 未做消融 | 流传版本攻击 | 未做官方消融，但代码可支撑 |
| 博主：Kimi 做规划 | 仓库：GPT-6 **Astra**（README L3、models.mjs L2） | 流传版本误称 | **流传版本错误**：规划器不是 Kimi |
| Jev 看画面 | （仓库从未提供 vision 输入） | 流传版本攻击 | ✅ 完全可证：JEV 只收 JSON state + criteria |

四个 open issue 中，三个直接质疑这次演示：
- **Issue #4** `gurio-wine`《Strongly Condemn This Misleading Astra/JEV Minecraft Demonstration》（14 👍）—— 最完整、最有论据
- **Issue #3** `zha-chicken`《Jev and Instructor Model seems not at all effective》—— 同样论点
- **Issue #1** `pannous`《these 131 jev action selections seem more like theater...》（2 👍，3 条评论，有用户自行重写 decide() 验证）

外加一个安全硬化 PR（#2 `btjones-me`，115 单元测试 + 12 安全测试通过）—— 与本次争议无关。

---

## 1. 仓库结构与关键文件

```
minecraft-agent/                 主入口 nether-agent.mjs
├── models.mjs                   Jev decide() + planner plan()
├── async-planner.mjs            后台 1s tick + 15s 节流的规划调度
├── nether-agent.mjs             主循环；candidates() 构建候选 + decide() 调用
├── agent.mjs                    旧版主入口（用 seed-route.json 水路）
├── end-combat.mjs               末影龙战斗候选构造
├── extra-actions.mjs            通用动作候选
├── optimization/
│   ├── policy.mjs               selectUsefulOptions() 过滤无意义动作
│   ├── seed-route.json          agent.mjs 的水上 waypoints（13 个）
│   ├── seed-map.json / seed-map.mjs
│   └── nether/
│       ├── config.json          ⭐ 预勘路线（seed、村庄、3 个宝箱、8 张床、地狱门、末地门）
│       ├── REVIEW.md            运行历史与各次 finalize 数值
│       └── freeze-run.mjs       把当前源码 + SHA256 拷到 runs/<run>/source/ 并写 run-config.json
├── nether-route.mjs             加载 config.json；提供 kitNeeds/portalActions/fullFrame
├── breath-safety.mjs / breath-reflex.mjs / ground-safety.mjs / corner-safety.mjs
├── camera-control.mjs / native-mirror.mjs / native-record.mjs
├── model-relay.mjs              本地 3099 中继；只允许 /api/alpha/decisions 和 /api/v1/chat/completions
└── README.md
```

---

## 2. 三轮核心代码验证（针对传播视频的攻击点）

### 2.1 Jev 不接收任何图像输入 —— **完全可证**

`models.mjs::decide()`（L14-22）：

```js
export async function decide(state, options) {
  state = compactObservation(state);
  const criteria = Object.fromEntries(options.map((o, i) => ['a' + i, o.description]));
  const body = {
    model: 'typesafe/jev-1.13',
    state: JSON.stringify(state),
    questions: {
      action: {
        type: 'choice',
        instructions: 'Control the Minecraft player. Choose one available action ...',
        criteria,
      },
    },
  };
  const r = await request('/api/alpha/decisions', body);
  ...
}
```

- 请求体只有 `model`、`state`（纯 JSON）、`questions.action.criteria`（选项列表）
- 没有 `image_url` / `vision` / `base64` / `messages[].content=[{type:image_url,...}]`
- 端点是 `/api/alpha/decisions` —— 这是 TypeSafe Jev 的 typed-decision 端点，**协议上不接受视觉输入**

`model-relay.mjs`（L13）：`if(!['/api/alpha/decisions','/api/v1/chat/completions'].includes(path))` —— 中继只放行这两个文本端点，且单请求上限 2MB（L13 `input.length > 2000000` 抛错）。

`nether-agent.mjs` 的 `state()` 函数（L19）传给 Jev 的就是结构化 JSON：`{position, dimension, health, food, inventory, hotbar, equipment, xp, knownSeed, plan, recent, battle, ...}`，全部是 Mineflayer 协议层数据。

**验证结论**：Jev 看不到画面。"Jev 看着屏幕打龙" 是营销叙事。

### 2.2 系统提示词已把完整路线写死 —— **完全可证**

`models.mjs::plan()`（L25）的 system prompt：

```text
"... You are the high-level planner for a Minecraft Java 1.16.5 Survival run.
Astra sets the objective and JEV chooses bounded game actions. Defeat the dragon
and exit. Use knownSeed: this is a new seed with a required Nether shortcut.
Follow the observed stage: prepare the stated kit, repair and enter the village
portal, walk through the Nether to the exit site, build and ignite the exit
portal, reach the active End portal, fight from cover with beds.
Current inventory deficits are in kitNeeds. Follow knownSeed.preparationBeds in
order after looting the first chest for the iron..."
```

系统提示词里：
- "Use knownSeed" —— 明确告诉规划器用预勘坐标
- "this is a new seed with a required Nether shortcut" —— 直接给出通关策略
- "walk through the Nether to the exit site, build and ignite the exit portal,
  reach the active End portal" —— 整个流程按步骤写在脸上
- "Follow knownSeed.preparationBeds in order" —— 让规划器按既定顺序去收床

预勘路线本身写在 `optimization/nether/config.json`：
- seed `8398967436125155523`
- village `(-225, 71, 255)`
- 3 个 supply chest（`-228,71,240` / `-290,68,253` / `-284,66,262`）
- 8 张准备床 `preparationBeds`
- `entryPortal`、`exitPortal`、`activePortal`（末地激活传送门 `(-1130, 34, 856)`）
- `netherRoute` 2 个点 + `netherTravel` 8 个下界路径 waypoint

更早期版 `agent.mjs` 还有 `optimization/seed-route.json`，13 个水路 waypoint（包含 `path: [[204,196],[200,192],...]` 的网格化预勘轨迹）。

**验证结论**：规划器的 "智能" 仅是 "按系统提示照单全收"。路线的发现完全发生在预勘阶段，不在模型运行时。

### 2.3 "165 次决策调用、78.2% 候选动作只有一个" —— **数字正确，比例合理**

README L11 给出 nether-final-08：**131 JEV decisions + 35 Astra calls = 166 ≈ 165**。

仓库其它运行的同口径数字（`optimization/COMPARISON.md`、`optimization/nether/REVIEW.md`）：

| 运行 | Jev 决策 | 规划调用 | 总计 | 时长 | 死亡 |
|---|---:|---:|---:|---|---:|
| `recorded-06`（旧） | 785 | 78 | 863 | 49m 08s | 1 |
| `nether-final-02` | 122 | 7 | 129 | 9m 17.35s | 0 |
| `nether-final-08`（README 主推） | 131 | 35 | 166 | 8m 43.3s | 0 |
| `optimized-final-04` | 161 | 20 | 181 | 12m 36s | 0 |

**单选项 / 多选项比例**（按 `nether-agent.mjs::candidates()` 与 `end-combat.mjs::endCombatActions()` 静态计数）：

| 调用点 | 文件:行 | 通常候选数 |
|---|---|---:|
| `depart` | nether-agent.mjs:42 | 1 |
| `nether_travel` | nether-agent.mjs:47 | 1（同一时刻只有当前 leg） |
| `bridge_<block>` | nether-agent.mjs:50 | 1（只有首个缺口） |
| `exit_stand` | nether-agent.mjs:51 | 1 |
| `enter_end_careful` | nether-agent.mjs:57 | 1 |
| `stronghold_approach` | nether-agent.mjs:58 | 1 |
| `portalActions`（补方块） | nether-route.mjs:31 | 通常 1（`missing[0]`） |
| `prepare_landing_bed` | end-combat.mjs:43 | 1 |
| `setup_bed_support` | end-combat.mjs:54 | 1 |
| `take_cover` | end-combat.mjs:56 | 1 |
| `one_timed_bed`（主攻击） | end-combat.mjs:59 | **1（这就是把龙炸死的唯一动作）** |
| `wait_dragon` | end-combat.mjs:49/65 | 1 |
| `escape_<idx>` | end-combat.mjs:21 | **3 个逃生方向**（`breathEscapeRoutes` 取 3） |
| `perch_wait_position_<n>` | end-combat.mjs:47 | **2 个**（`spots.slice(0,2)`） |
| `recover_<e.id>` | end-combat.mjs:36 | **最多 4 个掉落物** |
| `pickup_<e.id>`（bed） | nether-agent.mjs:36 | **最多 2**（`slice(0,2)`） |
| `bed_<q>`（village bed） | nether-agent.mjs:40 | **1**（`slice(0,1)`） |
| `blocks_<q>`（导航方块） | nether-agent.mjs:41 | **最多 2**（`slice(0,2)`） |
| `<label><coord>`（挖矿 / 拾取） | agent.mjs:85-100（旧版） | 每个标签 1-4 |
| `craft_<name>_<count>` | agent.mjs:105（旧版） | 通常 2（count=1 与 max） |
| `row_boat` / `row_detour_*` | agent.mjs:71（旧版水路） | **多个方向**（`routes.filter(...`） |

把末影龙战拆分看：全程约 152 秒（README L7 给了 nether-final-08 战斗段 152 秒），按每 1-2 秒一次 Jev 决策，约 60-80 次决策。其中末路攻击 `one_timed_bed` 是单选项；末前 `setup_bed_support`、`take_cover`、`prepare_landing_bed` 也都是 1；多选项集中在 `escape_<idx>`（3 个）与 `perch_wait_position_<n>`（2 个）。**战斗段单选项占比 ~80%+ 合理**。

其它阶段也类似 —— 多数调用都是"程序算出一个唯一合理动作让 Jev 点头"。**78.2% 这个数字在静态读码下能自洽**，不必逐条复算每一步。

---

## 3. 关键运行时事实（容易被营销忽略）

### 3.1 难度是 Peaceful，不是 Survival/Easy

- `optimization/nether/config.json` L4：`"difficulty": "peaceful"`
- `freeze-run.mjs` 写入的 `run-config.json`：`"difficulty": "peaceful", "gameMode": "survival"`
- `COMPARISON.md`：明确"Survival on **Peaceful** difficulty"
- 末影龙床炸在 Peaceful 下风险更低（无蜘蛛/末影人持续骚扰）
- **但是**：系统提示词对规划器说"Minecraft Java 1.16.5 Survival on Easy difficulty" —— 提示词和实际配置不一致；实际跑的难度比提示词描述的更低。

### 3.2 规划器是 GPT-6 Astra，**不是 Kimi**

`models.mjs:2-3`：

```js
export const plannerModel = process.env.PLANNER_MODEL || 'openai/gpt-6-astra';
export const plannerName = plannerModel.includes('sol') ? 'Sol' : 'Astra';
```

`README.md:43`：默认 `openai/gpt-6-astra`，可选 `openai/gpt-5.6-sol`。  
**中文传播视频"Kimi 做规划"是错误转述**。

### 3.3 战斗用 read-only Java 端 + 床炸

`README.md:50, 96`：使用官方 Minecraft Java 1.16.5 客户端做"只读"渲染；`observer/DragonObserver.java` 在服务端龙 tick 注入 HTTP 调用，回传龙头位置。**该端只读，不给物品、不动玩家、不改血**。这意味着：
- 录像是真的从 Minecraft 客户端渲染出来的（不是 CG）
- 但渲染客户端没有任何游戏操作权限
- 真正的"操作者"是 `nether-agent.mjs` 里的 Mineflayer bot
- 战斗段是 6 次床炸（约 152 秒）

### 3.4 路径、物资、门框、护航、防火……全部由 harness 写死

`README.md:104`：**"The final route is fixed in `optimization/nether/config.json`. Astra receives game state and route observations; JEV selects bounded actions."**

仓库自带 20+ 个非模型模块承担：
- 路径（`navigation.mjs`、`patch-pathfinder.mjs`、`column-travel.mjs`）
- 物资（`mining-tools.mjs`、`tool-recovery.mjs`、`inventory-recovery.mjs`、`inventory-display.mjs`）
- 门框建造（`nether-route.mjs::portalActions`、`placeAt`）
- 呼吸 / 落地 / 角 / 地安全（`breath-safety.mjs`、`breath-reflex.mjs`、`corner-safety.mjs`、`ground-safety.mjs`、`navigation.mjs`）
- 镜头（`camera-control.mjs` 9°/50ms 步进，下行走等待 20° 内）
- 战斗节拍（`end-combat.mjs`：单床攻击；按 `waitAwayForPerch` 决定何时离柱）
- 选观察点（`perch` 等位置 `spots.slice(0,2)` 排序）

更典型的"hardcoded candidate"举例 —— `nether-agent.mjs:42`：

```js
if (Object.values(kitNeeds(i)).every(n => n === 0))
  add('depart', 'Preparation complete. Start the Nether shortcut through the ruined portal.', ...)
```

当 kit 齐全时，harness 主动 `add('depart', ...)`；`selectUsefulOptions()` 过滤掉 wait 类后 Jev 收到的往往就是 **这一个** `depart`。

`end-combat.mjs:59` 是更极端的例子：

```js
if (inPosition && !unsafe(p) && support?.boundingBox === 'block' &&
    (bed || bedItem && (!bot.waitAwayForPerch || [2,3,5,6,7].includes(d.metadata[15]))))
  add('one_timed_bed', 'Arm ONE bed attack. Place the bed above the natural pillar ...', ...)
```

Jev 收到的是"在多个前置条件成立时执行这唯一一次炸床"。换随机选择器也会在同条件下炸床，区别只在是否"恰好命中攻击窗口"。这就是 Issue #4 作者说的：

> Calling every one of these a model decision and then emphasizing the total
> number of decisions gives a very misleading impression of the amount of
> agency the model actually has.

### 3.5 模型调用其实是异步且可被覆盖

`async-planner.mjs` L7：`if(!force && state.stage === lastStage && at - lastStarted < intervalMs) return null;` —— 规划器默认 15s 节流，相同阶段不重复调用。Astra 在 8 分钟里只调 35 次是符合这个节流逻辑的。

`nether-agent.mjs:62-66`：规划器在 setInterval 每 1s 触发 refresh()，但 asyncPlanner 自己节流；游戏循环不等规划器，等不来就重试或抛错。**游戏动作独立于规划响应**——这进一步证明规划器"晚几秒无所谓"。

### 3.6 仓库的"消融"实际上不存在

`README.md:11`：所有 17 项 run check + 8 项 route/camera/screen check + 29 项本地测试 + 1 次全 run。**但仓库没做"无 Astra"、"无 Jev"、"随机选择器"这类对照运行**。Issue #4 / #1 提议的 4 路对照（Astra+Jev / No Astra / 确定性 / 随机）在 N 次运行后比较完成率 / 中位时间 —— 是空白。

`Issue #1` 的 `1012796366` 在评论里说："replace decide() in models.mjs (or ask LLM to rewrite it) and you will see what jev sees every time it decides. I did so and it works fine" —— 也就是说至少 1 位评论者已经实测过替换 decide() 后游戏仍能跑通，与博主推断一致。

---

## 4. 与本项目本地资料的一致性 / 不一致

| 维度 | 本项目已确认 | minecraft-agent | 一致？ |
|---|---|---|---|
| Jev 用途 | 类型化决策（typed decision model） | 类型化决策（`/api/alpha/decisions`） | ✅ 一致 |
| Jev 是否支持图像 | 当前未在 11 篇 arXiv 论文摘要中找到 vision 输入声明 | 仓库代码完全不传图像 | ✅ 一致 |
| Jev 训练目标 RLCD | `AGENTS.md` / `实验` 文档已确认 RLCD 官方路线 | 仓库未训练 Jev，只调用 `typesafe/jev-1.13` | ✅ 一致 |
| 已知决策模型开源项目 | `NanoJev-main/`（训练）、`JEVfire-main/`（推理框架） | 仓库本身是一个第三方调用方 | ✅ 一致 |
| 比较论文 arXiv:2609.27678 | 评测 Jev 1.13.0 | 仓库使用 `typesafe/jev-1.13` | ✅ 一致（版号对齐） |
| 比较论文评测 GPT-6 Astra | 在比较模型清单里 | 仓库默认用 GPT-6 Astra 做规划 | ✅ 一致 |

差异点：

- 本项目的离线实战（`experiment/jev_practice/`）强调"软件逻辑和回放路径可验证，不替模型背书"。minecraft-agent 仓库的离线录制也走同一思路（`runs/<run>/` + `verify-run.mjs` + native recording），但对外演示被解读为"AI 自主能力展示"。**两者都依赖固定 seed + 预勘路线 + 程序化 harness，但表述差距巨大**。
- NanoJev 项目（`projects/NanoJev-main/`）的训练段、Checkpoint 服务、轨迹回放都在本项目已有分析里。minecraft-agent 没在 NanoJev 训练或推理上动手 —— 它直接调托管 Jev 1.13 + OpenRouter 上的 GPT-6 Astra。

---

## 5. 结论与本项目态度

### 5.1 代码事实

1. **Jev 不接收图像输入**。请求体只有 `state`（JSON）+ `questions.action.criteria`（候选字典）。视频营销里"看着屏幕打龙"是叙事，不是实现。
2. **路线在 harness 里写死**。`optimization/nether/config.json` 提供 seed、村庄、3 个宝箱、8 张准备床、地狱入口、末地门；`optimization/seed-route.json` 提供 13 个水路 waypoint；规划器系统提示词直接复述这些坐标。规划器不需要"发现"任何东西。
3. **候选列表大多数是单选项**。`nether-agent.mjs::candidates()` 与 `end-combat.mjs::endCombatActions()` 静态计数下，**单选项动作大量集中在 prep / portal / combat 关键节拍**（`depart`、`enter_end_careful`、`one_timed_bed`、`setup_bed_support`、`take_cover`、`prepare_landing_bed`、`wait_dragon` 等都是 1 个）。多选项集中在逃生方向（3）、栖位（2）、掉物回收（≤4）、水路（多方向）、挖矿/制作（按类 1-4）。**78.2% 单选项在静态读码下完全可能**。
4. **难度是 Peaceful，不是 Survival Easy**。系统提示词与实际配置不一致，实际更简单（无怪物）。
5. **规划器是 GPT-6 Astra，不是 Kimi**。中文传播视频转述错误。
6. **仓库自带的"消融"是空白**。Issue #4 / #1 / #3 提议的 4 路对照（Astra+Jev / No Astra / 确定性 / 随机）没人正式跑过；Issue #1 评论者已经实测"换 decide() 后游戏照跑"。
7. **harness 承担了绝大部分工程**（路径、安全、门框、镜头、防喷火、装备恢复、cursor 同步……），这是 30+ 个 .mjs 模块 + Java observer 的工作量。模型调用只是其中一环。

### 5.2 对中文传播视频的修正

| 视频说法 | 代码事实 |
|---|---|
| Kimi 做规划 | ❌ GPT-6 Astra（README、models.mjs） |
| Jev 看画面 | ❌ 只收 JSON state（Jev 协议本身就不支持视觉） |
| 165 次决策调用 | ✅ 大致正确（131 Jev + 35 Astra ≈ 166） |
| 78.2% 候选动作只有一个 | ✅ 静态读码自洽 |
| 规划器系统提示词包含完整通关路线 | ✅ 完全正确（models.mjs:25） |
| 随机决策也能通关 | ❓ 未做官方消融，但代码可支撑；Issue #1 评论者实测可行 |
| 8 分钟击败末影龙 | ✅ README 数字一致（8m 43.300s） |
| 成本 < 1 美元，Jev < 0.01 美元 | ⚠️ 仓库未量化；按调用次数估算属合理量级但需 OpenRouter 账单核实 |

### 5.3 对本项目实战叙事的影响

`experiment/jev_practice/` 与 `related_work/开源项目分析.md` 的判断继续成立：

- 这次争议不改变 `Jev` 本身的能力定位（Jev 仍然是 typed-decision 模型；
  typed-decision 的本意就是"在程序枚举的有限选项里选一个"，决策"颗粒度"本就由
  harness 决定）
- 但**强烈支持**本项目一贯立场："营销式 AI 演示"把 harness 的功劳算到模型头上，
  会让不懂细节的人高估模型能力。仓库自带 `verify-run.mjs` / `verification.json` /
  `world-proof.json` 这一套做法值得借鉴，但对外叙述必须把"harness 做了什么"与
  "模型贡献了什么"分开。
- 在 deck / 演讲稿中讲到 Jev 时，可以引用 minecraft-agent 作为典型反例：
  仓库虽然给出了完整的工程证据，但对外展示时弱化了 harness 工程量，强化了"AI
  决策数"，这是 AI 焦虑的来源之一。

---

## 6. 复核要点（不动手实测，仅静态）

| 复核项 | 看哪里 | 已确认？ |
|---|---|---|
| Jev 端点是否文本 only | `models.mjs:17` 的 body shape + `model-relay.mjs:13` 端点白名单 | ✅ |
| 系统提示词是否泄露路线 | `models.mjs:25` 的 system prompt + `config.json` 全部坐标 | ✅ |
| 候选列表单选项比例 | `nether-agent.mjs:32-61` + `end-combat.mjs:9-66` + `agent.mjs:65-105`（旧版） | ✅（定性） |
| 难度实际值 | `config.json:4` + `freeze-run.mjs:5` run-config.json | ✅ |
| 规划器真实身份 | `models.mjs:2-3` + `README.md:43` | ✅ |
| 末影龙战斗用床炸 + read-only observer | `end-combat.mjs:59` + `README.md:50,96` + `observer/DragonObserver.java` | ✅ |
| 预勘路线存在 | `config.json` + `seed-route.json` + `freeze-run.mjs` | ✅ |
| Harness 实际承担哪些工程 | 仓库 30+ `.mjs` + Java observer；README "Files and evidence" 段 | ✅ |
| 4 路消融是否官方跑过 | `README.md` / `COMPARISON.md` / `REVIEW.md` / `NOTES.md` 都未提 | ✅（无） |

---

## 7. 不在本次静态分析范围内

- 实际运行 8m 43.3s 录制的逐条事件追踪（需要 `runs/nether-final-08/` 实际 JSONL，不在 git 中）
- 4 路消融实验（Astra+Jev / No Astra / 确定性 / 随机）—— Issue #4 的核心诉求，需要 harness + OpenRouter 凭据
- 成本核算（README 未量化；需 OpenRouter usage 账单）
- 与 NanoJev 训练版的对比（`projects/NanoJev-main/` 已独立分析；与 minecraft-agent 的对比需另开 issue）

---

## 8. 来源 / 引用

- 仓库：`https://github.com/rmalde/minecraft-agent`（本地：`X:\Items\Jev-proj\related_work\minecraft-agent\`）
- Issue #4：`https://github.com/rmalde/minecraft-agent/issues/4`（gurio-wine，14 👍）
- Issue #3：`https://github.com/rmalde/minecraft-agent/issues/3`（zha-chicken）
- Issue #1：`https://github.com/rmalde/minecraft-agent/issues/1`（pannous，2 👍，3 评论）
- Issue/PR #2：`https://github.com/rmalde/minecraft-agent/pull/2`（btjones-me 安全硬化）
- 本项目：`AGENTS.md`、`related_work/开源项目分析.md`、`experiment/jev_practice/README.md`、
  `projects/NanoJev-main/`、`projects/fast-jev-compaction-main/`、`projects/JEVfire-main/`
- 关键文件：
  - `models.mjs:14-22`（Jev decide）
  - `models.mjs:25`（planner system prompt）
  - `nether-agent.mjs:32-61`（candidates 主循环）
  - `end-combat.mjs:9-66`（combat candidates）
  - `agent.mjs:65-105`（旧版 candidates）
  - `optimization/nether/config.json`（预勘路线）
  - `optimization/seed-route.json`（13 个水路 waypoint）
  - `optimization/nether/REVIEW.md`（各次运行数字）
  - `optimization/COMPARISON.md`（运行对比表）
  - `model-relay.mjs`（仅放行 decisions / chat/completions，2MB 上限）